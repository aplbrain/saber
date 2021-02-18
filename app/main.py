#!/usr/bin/python3

import tempfile
import subprocess
from subprocess import PIPE
import os
import datetime
import shutil
import yaml
import shutil
import zipfile

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    send_from_directory,
    abort,
    Response
)

from flask.json import dumps

from webportal.airflow_hook import trigger_dag, dag_run, dag_status, task_status
from webportal.s3_hook import (
    upload_file, 
    download_files,
    delete_folder, 
    download_file,
    get_batch_logs,
    list_repositories,
    list_images
)

import pandas as pd
from microns_analysis import analyze_experiment


APP = Flask(__name__)
APP.config["TEMPLATES_AUTO_RELOAD"] = True

JOB_DIR = "/opt/saber/jobs"
EXPERIMENT_DIR = "/opt/saber/experiments"
LOG_DIR = "/home/lowmaca1/saber/volumes/logs"
CONFIG_FILE = "/home/lowmaca1/saber/conduit/config/aws_config.yml"

WORKFLOW_DIR = "/opt/saber/cwl-workflows"
TOOL_TEMPLATE_PATH = WORKFLOW_DIR + "/run_algorithm.cwl.template"

S3_OUTPUT_BUCKET = "microns-saber"


# home page
@APP.route("/", methods=["GET", "POST"])
def home_page():
    return render_template("home_page.html")


@APP.route("/new_experiment", methods=["GET", "POST"])
def new_experiment():
    return render_template(
        "new_experiment.html",
        experiments=os.listdir(EXPERIMENT_DIR),
    )


@APP.route("/new_job", methods=["GET", "POST"])
def new_job():
    ls_output = subprocess.run(
        ["docker", "image", "ls", "--format", "'{{.Repository}}:{{.Tag}}'"],
        check=True,
        stdout=subprocess.PIPE,
    )
    docker_images = (
        ls_output.stdout.decode("utf-8").strip().replace("'", "").split("\n")
    )

    available_images = []
    for image in docker_images:
        rep, tag = image.split(":")
        if "256215146792.dkr.ecr.us-east-1.amazonaws.com" in rep and tag not in ["s3", "<none>"]:
            available_images.append(image)

    return render_template(
        "new_job.html",
        docker_images=available_images,
        experiments=os.listdir(EXPERIMENT_DIR),
    )


@APP.route("/experiments", methods=["GET", "POST"])
def view_experiments():
    exp_list = []
    for exp in os.listdir(EXPERIMENT_DIR):
        # load yamls for job and exp
        with open(os.path.join(EXPERIMENT_DIR, exp, "args.yaml"), "r") as ed:
            exp_details = yaml.load(ed)
        with open(os.path.join(EXPERIMENT_DIR, exp, "metadata.yaml"), "r") as ed:
            exp_metadata = yaml.load(ed)

        exp_details["name"] = exp
        exp_details["date"] = exp_metadata["date"]

        exp_list.append(exp_details)

    exp_list = sorted(
        exp_list,
        reverse=True,
        key=lambda x: datetime.datetime.strptime(x["date"], "%a %b %d %H:%M:%S %Y"),
    )
    return render_template(
        "experiments.html", experiments=exp_list, experiment_dir=EXPERIMENT_DIR
    )


# new job page
@APP.route("/jobs", methods=["GET", "POST"])
def view_jobs():
    job_list = []
    for job in os.listdir(JOB_DIR):
        # load yamls for job and exp
        try:
            with open(os.path.join(JOB_DIR, job, "job_details.yaml"), "r") as jd:
                job_details = yaml.load(jd)
            with open(os.path.join(JOB_DIR, job, "args.yaml"), "r") as ed:
                exp_details = yaml.load(ed)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            continue

        # get dag status
        last_status = job_details.get("status")
        if last_status is None:
            try:
                # get status from airflow
                job_details["status"] = dag_status(
                    "localhost",
                    "8080",
                    job_details["dag_id"],
                    job_details["execution_date"],
                )
                
                # save terminal state to job_details file
                if job_details["status"] == "success" or job_details["status"] == "failed":
                    with open(os.path.join(JOB_DIR, job, "job_details.yaml"), "w") as jd:
                        jd.write(
                            yaml.dump(job_details)
                        )
            except Exception as e:
                print(e)
                job_details["status"] = "Not Available"

        job_details["formatted_date"] = datetime.datetime.strptime(job_details["execution_date"], "%Y-%m-%dT%H:%M:%S").ctime()
        job_details["docker_image"] = job_details["docker_image"].replace("256215146792.dkr.ecr.us-east-1.amazonaws.com/", "").replace("/", "_").replace(":", "_")
        job_list.append(job_details)

    # sort by date
    job_list = sorted(
        job_list,
        reverse=True,
        key=lambda x: datetime.datetime.strptime(x["date"], "%Y_%m_%d-%H_%M_%S"),
    )

    return render_template("jobs.html", jobs=job_list)

@APP.route("/statistics", methods=["GET"])
def statistics():
    job_details_by_job = {}
    exp_details_by_job = {}

    for job in os.listdir(JOB_DIR):
        try:
            with open(os.path.join(JOB_DIR, job, "job_details.yaml"), "r") as jd:
                job_details = yaml.load(jd)
            with open(os.path.join(JOB_DIR, job, "args.yaml"), "r") as ed:
                exp_details = yaml.load(ed)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            continue

        try:
            job_details["info"] = dag_run("localhost", "8080", job_details["dag_id"], job_details["execution_date"])
        except Exception as e:
            print(f"Error:{e}")
            continue

        job_details_by_job[job] = job_details
        exp_details_by_job[job] = exp_details

    ls_output = subprocess.run(
            ["docker", "image", "ls", "--format", "'{{.Repository}}:{{.Tag}}:{{.Size}}'"],
        check=True,
        stdout=subprocess.PIPE,
    )
    docker_images = (
        ls_output.stdout.decode("utf-8").strip().replace("'", "").split("\n")
    )

    image_stats = {}
    num_jobs = 0
    num_trials = 0
    job_stats = []

    for image in docker_images:
        rep, tag, size = image.split(":")
        if "256215146792.dkr.ecr.us-east-1.amazonaws.com" in rep and tag not in ["s3", "<none>"]:
            image_id = rep + ":" + tag
            image_stats[image_id] = {
                "image_id": image_id,
                "image_size": size,
                "num_jobs": 0,
                "num_successful_jobs": 0,
                "num_trials": 0,
                "avg_exe_time": 0,
            }
    
    job_results_to_download = []
    for job, job_details in job_details_by_job.items():
        analysis_path = os.path.join(JOB_DIR, job, "analysis.csv")
        if not os.path.exists(analysis_path) and job_details.get("status") == "success":
            job_results_to_download.append(job)

    buckets = []
    keys = []
    for job in job_results_to_download:
        job_details = job_details_by_job[job]
        bucket = job_details["experiment_details"]["_saber_bucket"]
        fn = job_details["experiment_details"]["output_file"]
        key = os.path.join(job, "algorithm.0", fn)

        buckets.append(bucket)
        keys.append(key)

    with tempfile.TemporaryDirectory() as directory:
        print(f"Downloading {len(keys)} results into {directory}")
        download_files(buckets, keys, directory)

        for job, bucket, key in zip(job_results_to_download, buckets, keys):
            _analyze(job, job_details_by_job[job], exp_details_by_job[job], os.path.join(directory, key))


    for job, job_details in job_details_by_job.items():
        exp_details = exp_details_by_job[job]

        stats = {
            "job_name": job,
            "experiment": job_details["experiment"],
            "docker_image": job_details["docker_image"],
            "num_trials": 0,
            "abs_error": 0,
            "mean_abs_error": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
            "AP": 0,
            "accuracy": 0,
        }


        image = job_details["docker_image"]
        if "info" in job_details and "state" in job_details["info"] and job_details.get("status") == "success":

            #start_t = datetime.datetime.strptime(job_details["info"]["start_date"], '%Y-%m-%dT%H:%M:%SZ')
            #end_t = datetime.datetime.strptime(job_details["info"]["end_date"], '%Y-%m-%dT%H:%M:%SZ')
            #exec_t = datetime.datetime.strptime(job_details["info"]["execution_date"], '%Y-%m-%dT%H:%M:%SZ')
            #run_seconds = (end_t - start_t).total_seconds()
            #print(start_t, end_t, exec_t)
            run_seconds = 0


            analysis_path = os.path.join(JOB_DIR, job, "analysis.csv")
            if os.path.exists(analysis_path):
                num_jobs += 1
                image_stats[image]["num_jobs"] += 1
                image_stats[image]["num_successful_jobs"] += 1
                image_stats[image]["avg_exe_time"] += run_seconds

                results = pd.read_csv(analysis_path).to_dict('index')[0]
                print(results)

                job_details["num_trials"] = results["n_trials"]
                num_trials += job_details["num_trials"]
                image_stats[image]["num_trials"] += num_trials

                stats["num_trials"] = results["n_trials"]
                stats["abs_error"] = results["abs_error"]
                stats["mean_abs_error"] = results["mean_abs_error"]
                stats["precision"] = results["precision"]
                stats["recall"] = results["recall"]
                stats["f1"] = results["f1"]
                stats["AP"] = results["AP"]
                stats["accuracy"] = results["accuracy"]
                job_stats.append(stats)

    for image, stats in image_stats.items():
        if stats["num_successful_jobs"] > 0:
            stats["avg_exe_time"] /= stats["num_successful_jobs"]

    return render_template(
        "statistics.html",
        num_jobs=num_jobs,
        num_trials=num_trials,
        image_stats=list(image_stats.values()),
        job_stats=job_stats,
    )

def _analyze(job, job_details, exp_details, results_path):
    exp_metadata_path = os.path.join(EXPERIMENT_DIR, job_details["experiment"], "metadata.yaml")
    if not os.path.exists(exp_metadata_path):
        print(f"Skipping analysis of {job}... missing exp metadata.yaml @ {exp_metadata_path}")
        return

    with open(exp_metadata_path) as fp:
        metadata = yaml.load(fp)
        labels_path = None
        for fname in metadata["additional_files"]:
            if "labels" in fname:
                labels_path = os.path.join(EXPERIMENT_DIR, job_details["experiment"], fname)
                break

    if labels_path is None or not os.path.exists(labels_path):
        print(f"Skipping analysis of {job}... missing label file @ {labels_path}")
        return

    if results_path is None or not os.path.exists(results_path):
        print(f"Skipping analysis of {job}... missing result file @ {results_path}")
        return
    try:
        analyze_experiment(labels_path, results_path, out_file=os.path.join(JOB_DIR, job, "analysis.csv"))
    except Exception as e:
        #import shutil
        import traceback
        #shutil.copy(results_path, f"{job}.results.csv")
        print(f"Skipping analysis of {job}... error in analyze_experiment")
        traceback.print_exc()
        #print(e)
    print(f"Analyzed {job}")

@APP.route("/new_image", methods=["GET", "POST"])
def new_image():
    repositories = {repo : list_images(repo) for repo in list_repositories()}
    total, used, free = map(lambda x: x // (2**30), shutil.disk_usage("/"))
    percent_used = round(100*(used/total), 1)
    return render_template(
        "new_image.html",
        repositories = repositories.keys(),
        image_json = dumps(repositories),
        disk_space = (percent_used, free)
    )

@APP.route("/api/experiment/<experiment_name>/delete", methods=["POST"])
def api_delete_experiment(experiment_name):
    print("Deleting ", experiment_name)
    # TODO: Clean up S3
    try:
        shutil.rmtree(os.path.join(EXPERIMENT_DIR, experiment_name))
    except OSError as e:
        print(f"Error: {experiment_name} - {e}.")
    
    delete_status = delete_folder(S3_OUTPUT_BUCKET, experiment_name)
    if not delete_status:
        print(f"Failed to delete experiment '{experiment_name}' from S3.'")
    
    return redirect(url_for("view_experiments"))


@APP.route("/api/job/<job_name>/delete", methods=["POST"])
def api_delete_job(job_name):
    print("Deleting ", job_name)
    # TODO: Clean up S3
    try:
        shutil.rmtree(os.path.join(JOB_DIR, job_name))
    except OSError as e:
        print(f"Error: {job_name} - {e}.")
    return redirect(url_for("view_jobs"))

@APP.route("/api/multi_download", methods=["POST"])
def api_multi_download():
    buckets = []
    keys = []
    for job in request.json['jobs']:
        try:
            with open(os.path.join(JOB_DIR, job, "job_details.yaml"), "r") as jd:
                job_details = yaml.load(jd)
        except FileNotFoundError as e:
            print(job)
            abort(404)

        bucket = job_details["experiment_details"]["_saber_bucket"]
        fn = job_details["experiment_details"]["output_file"]
        key = os.path.join(job, "algorithm.0", fn)

        buckets.append(bucket)
        keys.append(key)

    with tempfile.TemporaryDirectory() as directory:
        download_files(buckets, keys, directory)

        lines = []
        for job_name, key in zip(request.json['jobs'], keys):
            with open(os.path.join(directory, key)) as fp:
                print(fp.name)
                for line in fp:
                    line = line.strip()
                    lines.append(job_name + "," + line)

    with tempfile.NamedTemporaryFile(mode='w') as fp:
        fp.writelines('\n'.join(lines))
        fp.flush()
        os.fsync(fp.fileno())
        head, tail = os.path.split(fp.name)
        return send_from_directory(head, tail, as_attachment=True, attachment_filename="multi-download.csv")


@APP.route("/api/experiment/<experiment_name>/download", methods=["GET"])
def api_download_experiment(experiment_name):
    file_path = os.path.join(EXPERIMENT_DIR, experiment_name)
    try:
        return send_from_directory(
            file_path, filename=f"{experiment_name}.zip", as_attachment=True
        )
    except FileNotFoundError:
        abort(404)


@APP.route("/api/jobs/<job>/download", methods=["GET"])
def api_download_job(job):
    try:
        with open(os.path.join(JOB_DIR, job, "job_details.yaml"), "r") as jd:
            job_details = yaml.load(jd)
    except FileNotFoundError as e:
        print(job)
        abort(404)
    
    fn = job_details["experiment_details"]["output_file"]
    
    if not job_details["local"]:
        key = os.path.join(job, "algorithm.0", fn)
        bucket = job_details["experiment_details"]["_saber_bucket"]
        with tempfile.TemporaryDirectory() as directory:   
            status = download_file(bucket, key, directory)
            if status:
                return send_from_directory(directory, filename=fn, as_attachment=True)
            else:
                abort(404)
    else:
        local_path =  os.path.join("/opt/saber/", job, "algorithm.0")
        if os.path.exists(local_path):
            return send_from_directory(local_path, filename=fn, as_attachment=True)


@APP.route("/api/experiment", methods=["POST"])
def api_new_experiment():

    # Request necessary params
    experiment_name = request.form["name"]
    s3_images_bucket = request.form["s3ImagesBucket"]
    # s3_results_bucket = request.form["s3ResultsBucket"]
    s3_results_bucket = S3_OUTPUT_BUCKET
    experiment_csv = request.files["experiment"]
    
    # Create time-tagged directories and path variables
    time_tag = datetime.datetime.now().ctime()
    experiment_dir = f"{EXPERIMENT_DIR}/{experiment_name}/"
    os.makedirs(experiment_dir, exist_ok=True)
    
    csv_path = os.path.abspath(f"{experiment_dir}/experiment.csv")
    experiment_csv.save(csv_path)

    data_file_object_key = f"experiments/{experiment_name}/experiment.csv"
    train_file_object_key = f"experiments/{experiment_name}/train_file.json"

    # Check for additional and train files and save them to directory. 
    additional_files = []
    if "additional_files" in request.files:
        additional_files = request.files.getlist("additional_files")
    
    for additional_file in additional_files:
        additional_file.save(f"{experiment_dir}/{additional_file.filename}")
    
    train_file = None
    if "train_file" in request.files:
        train_file = request.files["train_file"]
        train_fp = f"{experiment_dir}/{train_file.filename}"
        train_file.save(train_fp)

    # Save experiment metadata in YAML file
    metadata_path = os.path.abspath(f"{experiment_dir}/metadata.yaml")
    with open(metadata_path, "w") as fp:
        fp.write(
            yaml.dump(
                {
                    "name": experiment_name,
                    "date": time_tag,
                    "additional_files": [f.filename for f in additional_files],
                    "train_file": train_file.filename if train_file else None
                }
            )
        )

    # Create SABER YAML file (args.yaml)
    args_path = os.path.abspath(f"{experiment_dir}/args.yaml")
    with open(args_path, "w") as fp:
        # Mode and output bucket are currently fixed.
        fp.write(
            yaml.dump(
                {
                    "test_datafile": {"class": "File", "path": data_file_object_key},
                    "train_datafile": {"class": "File", "path": train_file_object_key if train_file else None},
                    "images_dir": "s3://" + s3_images_bucket,
                    "output_file": None,
                    "params_file": "params.zip",
                    "_saber_bucket": s3_results_bucket,
                },
                default_flow_style=False,
            )
        )

    # save zipfile of all the files for downloading later
    with zipfile.ZipFile(f"{experiment_dir}/{experiment_name}.zip", "w") as ezip:
        ezip.write(csv_path, "experiment.csv")
        ezip.write(metadata_path, "metadata.yaml")
        ezip.write(args_path, "args.yaml")
        for additional_file in additional_files:
            ezip.write(
                os.path.abspath(f"{experiment_dir}/{additional_file.filename}"),
                additional_file.filename,
            )
        if train_file:
            ezip.write(
                os.path.abspath(f"{experiment_dir}/{train_file.filename}"),
                train_file.filename,
            )

    if train_file:
        status = upload_file(train_fp, s3_results_bucket, train_file_object_key)
        if not status:
            print("Unable to upload train file to s3. Check logs.")
            shutil.rmtree(experiment_dir)

    status = upload_file(csv_path, s3_results_bucket, data_file_object_key)
    if not status:
        print("Unable to upload experiment to s3. Check logs.")
        shutil.rmtree(experiment_dir)
        # TODO: Include pop-up error on app.

    return redirect(url_for("view_experiments"))


@APP.route("/api/job", methods=["POST"])
def api_new_job():
    # extract args from request
    docker_image = request.form["dockerImage"]
    experiment_tag = request.form["experiment"]
    cpu_config = request.form.get("cpu-toggle")
    local_config = request.form.get("local-toggle")

    # each job is tagged with submit time
    time_tag = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    sanitized_docker_image = docker_image.replace("256215146792.dkr.ecr.us-east-1.amazonaws.com/", "").replace("/", "_").replace(":", "_")

    job_name = f"{time_tag}-{experiment_tag}-{sanitized_docker_image}"

    # create this job's directory
    job_dir = f"{JOB_DIR}/{job_name}/"
    os.makedirs(job_dir, exist_ok=True)

    # copy cwl tool to job dir
    with open(TOOL_TEMPLATE_PATH) as fp:
        tool_template = fp.read()
    with open(os.path.join(job_dir, "run_algorithm.cwl"), "w") as fp:
        fp.write(tool_template.replace("{{dockerImageName}}", docker_image))

    yaml_path = os.path.join(EXPERIMENT_DIR, experiment_tag, "args.yaml")

    # specify output file name
    output_name = f"{job_name}.csv"

    if len(output_name) > 64:
        # Truncate name for SABER
        output_name = f"{sanitized_docker_image}_OUTPUT.csv"
    with open(yaml_path, "r") as exp_file:
        exp = yaml.load(exp_file)

    yaml_path = os.path.join(job_dir, "args.yaml")
    exp["output_file"] = output_name

    # Specify dag ID. This helps organize jobs in airflow by docker image. 
    train_wf = False
    dag_id = f"task_3_{sanitized_docker_image}"
    if exp["train_datafile"]["path"]:
        train_wf = True
        dag_id = f"task_3_with_train_{sanitized_docker_image}"

    # Specify CWL and copy to job dir
    if train_wf and local_config:
        cwl = "task_3_with_train_local.cwl"
    elif train_wf and not local_config:
        cwl = "task_3_with_train.cwl"
    elif not train_wf and local_config:
        cwl = "task_3_local.cwl"
    else:
        cwl = "task_3.cwl"

    shutil.copy(os.path.join(WORKFLOW_DIR, cwl), job_dir)
    cwl_path = os.path.join(job_dir, cwl)
    
    # write yaml file 
    with open(yaml_path, "w") as exp_file:
        exp_file.write(yaml.dump(exp))    
    
    # copy aws job config 
    if cpu_config:
        shutil.copy("config/aws_config_cpu.yml", CONFIG_FILE)
    else:
        shutil.copy("config/aws_config_gpu.yml", CONFIG_FILE)
    
    def work():
        yield f"Invoking conduit cli tools... {dag_id}\r\n"
        # invoke conduit cli tools
        p = subprocess.Popen(
            f"docker exec saber_cwl_parser_1 conduit parse {cwl_path} {yaml_path} --dag_id {dag_id} --build",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        )
        for line in p.stdout:
            yield "[DOCKER] " + line
        # wait for process to finish just to be sure
        p.wait()

        if p.returncode != 0:
            for line in p.stderr:
                yield "[ERROR] " + line

        yield f"Triggering airflow dag... {dag_id}\r\n"
        execution_date, dag_status = trigger_dag("localhost", "8080", dag_id)

        if dag_status == 200:
            job_details_path = os.path.join(job_dir, "job_details.yaml")
            yield f"Saving job details... {job_details_path}\r\n"
            # save job details to yaml file
            with open(job_details_path, "w") as fp:
                fp.write(
                    yaml.dump(
                        {
                            "job_name": job_name,
                            "date": time_tag,
                            "dag_id": dag_id,
                            "docker_image": docker_image,
                            "experiment": experiment_tag,
                            "execution_date": execution_date,
                            "experiment_details": exp,
                            "local": bool(local_config)
                        },
                        default_flow_style=False,
                    )
                )
            yield "Done!\r\n"

        else:
            # DAG Failed.
            shutil.rmtree(job_dir)
            yield f"DAG Failed to launch. Error Code: {dag_status}. Check logs in Airflow or contact dev team."

    return Response(work(), mimetype="text/plain")


@APP.route("/api/jobs/<job_name>/dag/<dag_id>/date/<execution_date>/log", methods=["GET"])
def api_download_log(job_name, dag_id, execution_date):
    # Specify file name and path of the log
    fn = f"{job_name}.log"
    fp = os.path.join(JOB_DIR, job_name, fn)
    
    # Pull most recent logs from AWS Batch. 
    with open(fp, 'w') as log:
        log_content = get_batch_logs(dag_id, execution_date, LOG_DIR)
        if log_content:
            log.write(log_content)
        else:
            log.write("No logs available. Check Airflow.")
    # Send file to user
    try:
        return send_from_directory(
            os.path.split(fp)[0], filename=fn, as_attachment=True
        )
    except FileNotFoundError:
        abort(404)


@APP.route("/api/pull_image", methods=["POST"])
def api_new_image():
    repository = request.form["repositoryName"]
    image_tag = request.form["imageName"]
    uri = f"256215146792.dkr.ecr.us-east-1.amazonaws.com/{repository}:{image_tag}"
    def work():
        yield(f"Pulling {repository}:{image_tag} from ECR \n")
        # invoke conduit cli tools
        p = subprocess.Popen(
            "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 256215146792.dkr.ecr.us-east-1.amazonaws.com",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
        )
        for line in p.stdout:
            yield "[AWS ECR] " + line  

        p = subprocess.Popen(
            f"docker pull {uri}",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        )
        for line in p.stdout:
            yield "[DOCKER] " + line
    
    return Response(work(), mimetype="text/plain")

if __name__ == "__main__":
    APP.run(debug=True)

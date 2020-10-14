#!/usr/bin/python3

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    send_from_directory,
    abort,
    Response,
)
import subprocess
from subprocess import PIPE
import os
import datetime
import shutil
import yaml
import shutil
import zipfile

from webportal.airflow_hook import trigger_dag, dag_status, task_status
from webportal.s3_hook import upload_file, delete_folder, generate_download_link, get_batch_logs

APP = Flask(__name__)
APP.config["TEMPLATES_AUTO_RELOAD"] = True

JOB_DIR = "/opt/saber/jobs"
EXPERIMENT_DIR = "/opt/saber/experiments"
LOG_DIR = "/home/lowmaca1/saber/volumes/logs"

WORKFLOW_DIR = "/opt/saber/cwl-workflows"
WORKFLOW_PATH = WORKFLOW_DIR + "/task_3.cwl"
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
        if "256215146792.dkr.ecr.us-east-1.amazonaws.com" in rep and "s3" == tag:
            tool = rep.split("/")[1:]
            available_images.append("/".join(tool))

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

    exo_list = sorted(
        exp_list,
        reverse=True,
        key=lambda x: datetime.datetime.strptime(x["date"], "%Y_%m_%d-%H_%M_%S"),
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
        try:
            job_details["status"] = dag_status(
                "localhost",
                "8080",
                job_details["dag_id"],
                job_details["execution_date"],
            )
        except:
            job_details["status"] = "Not Available"

        # get output download link
        bucket = exp_details["_saber_bucket"]
        key = os.path.join(
            job_details["experiment"], "algorithm.0", exp_details["output_file"]
        )

        job_list.append(job_details)

    # sort by date
    job_list = sorted(
        job_list,
        reverse=True,
        key=lambda x: datetime.datetime.strptime(x["date"], "%Y_%m_%d-%H_%M_%S"),
    )

    return render_template("jobs.html", jobs=job_list)


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

    bucket = job_details["experiment_details"]["_saber_bucket"]
    fn = job_details["experiment_details"]["output_file"]
    key = os.path.join(job, "algorithm.0", fn)

    return redirect(generate_download_link(bucket, key, 3000))


@APP.route("/api/experiment", methods=["POST"])
def api_new_experiment():
    experiment_name = request.form["name"]
    s3_images_bucket = request.form["s3ImagesBucket"]
    # s3_results_bucket = request.form["s3ResultsBucket"]
    s3_results_bucket = S3_OUTPUT_BUCKET
    experiment_csv = request.files["experiment"]
    if "additional_files" in request.files:
        additional_files = request.files.getlist("additional_files")
    else:
        additional_files = []

    time_tag = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    experiment_dir = f"{EXPERIMENT_DIR}/{experiment_name}/"
    os.makedirs(experiment_dir, exist_ok=True)

    csv_path = os.path.abspath(f"{experiment_dir}/experiment.csv")
    experiment_csv.save(csv_path)

    s3_object_key = f"{experiment_name}/experiment.csv"

    for additional_file in additional_files:
        additional_file.save(f"{experiment_dir}/{additional_file.filename}")

    metadata_path = os.path.abspath(f"{experiment_dir}/metadata.yaml")
    with open(metadata_path, "w") as fp:
        fp.write(
            yaml.dump(
                {
                    "date": time_tag,
                    "additional_files": [f.filename for f in additional_files],
                }
            )
        )

    args_path = os.path.abspath(f"{experiment_dir}/args.yaml")
    with open(args_path, "w") as fp:
        # Mode and output bucket are currently fixed.
        fp.write(
            yaml.dump(
                {
                    "mode": "3-test",
                    "data_file": {"class": "File", "path": s3_object_key},
                    "images_dir": "s3://" + s3_images_bucket,
                    "output_file": None,
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

    status = upload_file(csv_path, s3_results_bucket, s3_object_key)
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

    # each job is tagged with submit time
    time_tag = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    sanitized_docker_image = docker_image.replace("/", "_")

    job_name = f"{time_tag}-{experiment_tag}-{sanitized_docker_image}"

    # create this job's directory
    job_dir = f"{JOB_DIR}/{job_name}/"
    os.makedirs(job_dir, exist_ok=True)

    # copy cwl workflow to job dir
    shutil.copy(WORKFLOW_PATH, job_dir)

    # copy cwl tool to job dir
    with open(TOOL_TEMPLATE_PATH) as fp:
        tool_template = fp.read()
    with open(os.path.join(job_dir, "run_algorithm.cwl"), "w") as fp:
        fp.write(tool_template.replace("{{dockerImageName}}", docker_image))

    cwl_path = os.path.join(job_dir, "task_3.cwl")
    yaml_path = os.path.join(EXPERIMENT_DIR, experiment_tag, "args.yaml")

    # specify output file name
    output_name = f"{job_name}.csv"
    with open(yaml_path, "r") as exp_file:
        exp = yaml.load(exp_file)

    yaml_path = os.path.join(job_dir, "args.yaml")
    exp["output_file"] = output_name
    with open(yaml_path, "w") as exp_file:
        exp_file.write(yaml.dump(exp))

    dag_id = f"task_3_{job_name}"

    def work():
        yield f"Invoking conduit cli tools... {cwl_path} {yaml_path}\r\n"
        # invoke conduit cli tools
        p = subprocess.Popen(
            f"docker exec saber_cwl_parser_1 conduit parse {cwl_path} {yaml_path} --build",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        )
        for line in p.stdout:
            yield "[DOCKER]" + line
        # wait for process to finish just to be sure
        p.wait()

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
                        },
                        default_flow_style=False,
                    )
                )
            yield "Done!\r\n"

        else:
            # DAG Failed.
            # shutil.rmtree(job_dir)
            yield f"DAG Failed to launch. Error Code: {dag_status}"

    return Response(work(), mimetype="text/plain")


@APP.route("/api/jobs/<job_name>/log", methods=["GET"])
def api_download_log(job_name):

    # Specify file name and path of the log
    fn = f"{job_name}.log"
    fp = os.path.join(JOB_DIR, job_name, fn)
    
    # Pull most recent logs from AWS Batch. 
    dag_id = f"task_3_{job_name}"
    with open(fp, 'w') as log:
        log_content = get_batch_logs(dag_id, LOG_DIR)
        if log_content:
            log.write(log_content)
    
    # Send file to user
    try:
        return send_from_directory(
            fp, filename=fn, as_attachment=True
        )
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    APP.run(debug=True)

#!/usr/bin/python3

from flask import Flask, render_template, redirect, request, url_for
import subprocess
import os
import datetime
import shutil
import yaml
import shutil

from webportal.airflow_hook import trigger_dag, dag_status, task_status
from webportal.s3_hook import upload_file, generate_download_link

APP = Flask(__name__)
APP.config["TEMPLATES_AUTO_RELOAD"] = True

JOB_DIR = "/opt/saber/jobs"
EXPERIMENT_DIR = "/opt/saber/experiments"

WORKFLOW_DIR = "/opt/saber/cwl-workflows"
WORKFLOW_PATH = WORKFLOW_DIR + "/task_3.cwl"
TOOL_TEMPLATE_PATH = WORKFLOW_DIR + "/run_algorithm.cwl.template"


# home page
@APP.route("/", methods=["GET", "POST"])
def home_page():
    return render_template("home_page.html")


@APP.route("/new_experiment", methods=["GET", "POST"])
def new_experiment():
    return render_template("new_experiment.html")


@APP.route("/experiments", methods=["GET", "POST"])
def view_experiments():
    exp_list = []
    for exp in os.listdir(EXPERIMENT_DIR):
        # load yamls for job and exp
        with open(os.path.join(EXPERIMENT_DIR, exp, "args.yaml"), 'r') as ed:
            exp_details = yaml.load(ed)

        exp_details["name"] = exp[:-20]
        exp_details["date"] = exp[-19:]

        exp_list.append(exp_details)
    
    exo_list = sorted(exp_list, key=lambda x: datetime.datetime.strptime(x['date'], '%Y_%m_%d-%H_%M_%S'))
    return render_template(
        "experiments.html",
        experiments=exp_list,
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
            tool = rep.split('/')[1:]
            available_images.append("/".join(tool))

    return render_template(
        "new_job.html",
        docker_images=available_images,
        experiments=os.listdir(EXPERIMENT_DIR),
    )


# new job page
@APP.route("/jobs", methods=["GET", "POST"])
def view_jobs():
    job_list = []
    for job in os.listdir(JOB_DIR):
        # load yamls for job and exp
        with open(os.path.join(JOB_DIR, job, "job_details.yaml"), 'r') as jd:
            job_details = yaml.load(jd)
        with open(os.path.join(EXPERIMENT_DIR, job_details["experiment"], "args.yaml"), 'r') as ed:
            exp_details = yaml.load(ed)

        # get dag status
        job_details["status"] = dag_status("localhost", "8080", job_details["dag_id"], job_details["execution_date"])
        
        # get output download link
        bucket = exp_details["_saber_bucket"]
        key = os.path.join(job_details["dag_id"], "algorithm.0", exp_details["output_file"])
        job_details['output'] = generate_download_link(bucket, key, 300)


        job_list.append(job_details)
    
    # sort by date
    job_list = sorted(job_list, key=lambda x: datetime.datetime.strptime(x['execution_date'], '%Y-%m-%dT%H:%M:%S'))
    
    return render_template(
        "jobs.html",
        jobs=job_list
        )


@APP.route('/api/experiment/<experiment_name>/date/<experiment_date>/delete', methods=['POST'])
def api_delete_experiment(experiment_name, experiment_date):
    delete_dir = experiment_name + "-" + experiment_date
    print('Deleting ', delete_dir)
    # TODO: Clean up S3
    try:
        shutil.rmtree(os.path.join(EXPERIMENT_DIR, delete_dir))
    except OSError as e:
        print(f"Error: {delete_dir} - {e}.")
    return redirect(url_for("view_experiments"))


@APP.route('/api/job/<job_name>/delete', methods=['POST'])
def api_delete_job(job_name):
    print('deleting', job_name)
    # TODO actually delete!
    return redirect(url_for('view_jobs'))


@APP.route("/api/experiment", methods=["POST"])
def api_new_experiment():
    experiment_name = request.form["name"]
    mode =  request.form["mode"]
    s3_images_bucket = request.form["s3ImagesBucket"]
    s3_results_bucket = request.form["s3ResultsBucket"]
    experiment_csv = request.files["experiment"]

    time_tag = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    experiment_dir = f"{EXPERIMENT_DIR}/{experiment_name}-{time_tag}/"
    os.makedirs(experiment_dir, exist_ok=True)

    csv_path = os.path.abspath(f"{experiment_dir}/experiment.csv")
    experiment_csv.save(csv_path)

    s3_object_key = f"saber/exp/{experiment_name}-{time_tag}/experiment.csv"
    status = upload_file(csv_path, s3_results_bucket, s3_object_key)
    if not status:
        # TODO : Decide on what error to return on upload fail
        pass

    with open(f"{experiment_dir}/args.yaml", "w") as fp:
        fp.write(
            yaml.dump(
                {
                    "mode": mode,
                    "dataFile": {"class": "File", "path": s3_object_key},
                    "imagesDir": "s3://" + s3_images_bucket,
                    "outputFile": f"{experiment_name}-{time_tag}-OUTPUT.txt",
                    "_saber_bucket": s3_results_bucket,
                },
                default_flow_style=False,
            )
        )

    return redirect(url_for("view_experiments"))


@APP.route("/api/job", methods=["POST"])
def api_new_job():
    # extract args from request
    job_name = request.form["jobName"]
    docker_image = request.form["dockerImage"]
    experiment_tag = request.form["experiment"]

    # each job is tagged with submit time
    time_tag = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    # create this job's directory
    job_dir = f"{JOB_DIR}/{job_name}-{time_tag}/"
    os.makedirs(job_dir, exist_ok=True)

    # copy cwl workflow to job dir
    shutil.copy(WORKFLOW_PATH, job_dir)

    # copy cwl tool to job dir
    with open(TOOL_TEMPLATE_PATH) as fp:
        tool_template = fp.read()
    with open(os.path.join(job_dir, "run_algorithm.cwl"), "w") as fp:
        fp.write(tool_template.replace("{{dockerImageName}}", docker_image))

    cwl_path = os.path.join(job_dir, "task_3.cwl")
    yaml_path = f"{EXPERIMENT_DIR}/{experiment_tag}/args.yaml"
    dag_id = f"task_3_{experiment_tag}"

    #  invoke conduit cli tools
    subprocess.run(
        f"docker exec saber_cwl_parser_1 conduit parse {cwl_path} {yaml_path} --build",
        shell=True,
    )
    execution_date, dag_status = trigger_dag("localhost", "8080", dag_id)

    # save job details to yaml file
    with open(os.path.join(job_dir, "job_details.yaml"), "w") as fp:
        fp.write(
            yaml.dump(
                {
                    "job_name": job_name,
                    "dag_id": dag_id,
                    "docker_image": docker_image,
                    "experiment": experiment_tag,
                    "execution_date": execution_date,
                },
                default_flow_style=False,
            )
        )

    return redirect(url_for("view_jobs"))


if __name__ == "__main__":
    APP.run(debug=True)

#!/usr/bin/python3

from flask import Flask, render_template, redirect, request, url_for
import subprocess
import os
import datetime
import shutil
import yaml

from webportal.airflow_hook import trigger_dag, dag_status, task_status
from webportal.s3_hook import upload_file, generate_download_link

APP = Flask(__name__)
APP.config['TEMPLATES_AUTO_RELOAD'] = True

JOB_DIR = '/opt/saber/jobs'
EXPERIMENT_DIR = '/opt/saber/experiments'

WORKFLOW_DIR = '/opt/saber/cwl-workflows'
WORKFLOW_PATH = WORKFLOW_DIR + '/task_3.cwl'
TOOL_TEMPLATE_PATH = WORKFLOW_DIR + '/run_algorithm.cwl.template'


#home page
@APP.route("/", methods=['GET', 'POST'])
def home_page():
    return render_template("home_page.html")


@APP.route('/new_experiment', methods=['GET', 'POST'])
def new_experiment():
    return render_template("new_experiment.html")


@APP.route('/experiments', methods=['GET', 'POST'])
def view_experiments():
    return render_template(
        "experiments.html",
        experiments=os.listdir(EXPERIMENT_DIR),
    )


@APP.route("/new_job", methods=["GET","POST"])
def new_job():
    ls_output = subprocess.run(
            ['docker', 'image', 'ls', '--format', "'{{.Repository}}:{{.Tag}}'"],
            check=True, stdout=subprocess.PIPE
    )
    docker_images = ls_output.stdout.decode('utf-8').strip().replace("'", "").split('\n')

    return render_template(
            "new_job.html",
            docker_images=docker_images,
            experiments=os.listdir(EXPERIMENT_DIR),
    )

#new job page
@APP.route("/jobs", methods=["GET","POST"])
def view_jobs():
    return render_template("jobs.html")


@APP.route("/api/experiment", methods=["POST"])
def api_new_experiment():
    experiment_name = request.form['name']
    s3_images_bucket = request.form['s3ImagesBucket']
    s3_results_bucket = request.form['s3ResultsBucket']
    experiment_csv = request.files['experiment']

    time_tag = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    experiment_dir = f'{EXPERIMENT_DIR}/{experiment_name}-{time_tag}/'
    os.makedirs(experiment_dir, exist_ok=True)

    csv_path = os.path.abspath(f'{experiment_dir}/experiment.csv')
    experiment_csv.save(csv_path)
    
    s3_object_key = f"saber/exp/{experiment_name}-{time_tag}/experiment.csv"
    status = upload_file(csv_path, s3_results_bucket, s3_object_key)
    if not status:
        # TODO : Decide on what error to return on upload fail
        pass
    
    with open(f'{experiment_dir}/args.yaml', 'w') as fp:
        fp.write(yaml.dump({
            'testDataFile': {"class":"file", "path": csv_path},
            'imagesDir': s3_images_bucket,
            'outputFile': s3_results_bucket,
            '_saber_bucket': s3_results_bucket
        }))

    return redirect(url_for('view_experiments'))


@APP.route("/api/job", methods=["POST"])
def api_new_job():
    # extract args from request
    job_name = request.form['jobName']
    docker_image = request.form['dockerImage']
    experiment_tag = request.form['experiment']

    # each job is tagged with submit time
    time_tag = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    # create this job's directory
    job_dir = f'{JOB_DIR}/{job_name}/{time_tag}/'
    os.makedirs(job_dir, exist_ok=True)

    # copy cwl workflow to job dir
    shutil.copy(WORKFLOW_PATH, job_dir)

    # copy cwl tool to job dir
    with open(TOOL_TEMPLATE_PATH) as fp:
        tool_template = fp.read()
    with open(f'{job_dir}/run_algorithm.cwl', 'w') as fp:
        fp.write(tool_template.replace('{{dockerImageName}}', docker_image))

    yaml_path = f'{EXPERIMENT_DIR}/{experiment_tag}/args.yaml'

    # TODO invoke conduit cli tools
    subprocess.run("docker exec saber_cwl_parser_1 conduit parse {WORKFLOW_PATH} {yaml_path}", shell=True)
    trigger_dag(FLASK_IP, 8080, )
    
    return redirect(url_for('view_jobs'))


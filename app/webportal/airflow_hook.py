#!/usr/bin/env python3

from requests import put, get, post
import json
import time

def trigger_dag(ip, port, dag_id):
    '''
    Trigger a DAG.
    Uses custom API developed by SABER team.

    Arguments:
        ip (str): ip address
        port (str): port for Airflow (saber_webserver_1 container)
        dag_id (str): the DAG ID

    Returns:
        execution_date (str): execution date with format 'YYYY-mm-DDTHH:MM:SS'
    '''
    max_tries = 3
    current_tries = 0
    done = False
    url = 'http://' + ip + ':' + port + '/dags/' + dag_id + '/run'
    payload = json.dumps({})
    
    while not done:
        current_tries += 1
        response = post(url, data = payload)
        print('Trigger dag status code: ' + str(response.status_code) + ' ' + response.reason)
        if response.status_code != 200 and current_tries < max_tries: 
            print('Dag did not launch successfully. Error ' + str(response.status_code))
            print('Trying again.... ')
            time.sleep(10)
        elif response.status_code != 200 and current_tries >= max_tries:
            print('Dag did not launch successfully. Error ' + str(response.status_code))
            print('Exiting loop...')
            return None, response.status_code
        else: 
            trigger_dag_status = response.status_code
            print('Response dictionary from triggering dag: ' + str(response.json()))
            index = response.json()['message'].find('manual__')
            execution_date = response.json()['message'][index + 8 : index + 8 + 19]
            print('Execution date of the DAG: ' + execution_date)
            done = True
    
    return execution_date, trigger_dag_status

def dag_run(ip, port, dag_id, execution_date):
    '''
    Get the status of a particular DAG run.
    Uses custom API developed by SABER team.

    Arguments:
        ip (str): ip address
        port (str): port for Airflow (saber_webserver_1 container)
        dag_id (str): the DAG ID
        execution_date (str): execution date with format 'YYYY-mm-DDTHH:MM:SS'

    Returns:
        dag_run_status (str): the status of the specified DAG run
    '''
    url = 'http://' + ip + ':' + port + '//api/experimental/dags/' + dag_id + '/dag_runs/' + execution_date
    payload = {}
    response = get(url, data = json.dumps(payload))
    return response.json()

def dag_status(ip, port, dag_id, execution_date):
    '''
    Get the status of a particular DAG run.
    Uses custom API developed by SABER team.

    Arguments:
        ip (str): ip address
        port (str): port for Airflow (saber_webserver_1 container)
        dag_id (str): the DAG ID
        execution_date (str): execution date with format 'YYYY-mm-DDTHH:MM:SS'

    Returns:
        dag_run_status (str): the status of the specified DAG run
    '''
    url = 'http://' + ip + ':' + port + '/dags/' + dag_id + '/dag_runs/' + execution_date
    payload = {}
    response = get(url, data = json.dumps(payload))
    dag_run_status = response.json()['state']
    return dag_run_status

def task_status(ip, port, dag_id, execution_date, task_id):
    '''
    Get the status of a particular task.
    Uses experimental API.

    Arguments:
        ip (str): ip address
        port (str): port for Airflow (saber_webserver_1 container)
        dag_id (str): the DAG ID
        execution_date (str): execution date with format 'YYYY-mm-DDTHH:MM:SS'
        task_id = the task ID

    Returns:
        status_task (str): the status of the specified task
    '''
    url = 'http://' + ip + ':' + port + '/api/experimental/dags/' + dag_id + '/dag_runs/' + execution_date + '/tasks/' + task_id
    payload = {}
    response = get(url, data = json.dumps(payload))
    # print(response.json())
    print(response.status_code, response.reason)
    status_task = response.json()['state']
    return status_task

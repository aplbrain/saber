from subprocess import run

def parse_job(cwl_path, job_path):
    """
    Runs CLI commands to parse a job.
    """
    run("docker exec saber_cwl_parser_1 conduit parse {cwl_path} {job_path}", shell=True)
    




import yaml
import os
from contextlib import contextmanager
def load_data(path):
    with open(path) as fp:
        test_data = yaml.load(fp)
    return test_data
def resolve_filename(*path):
    fileloc = os.path.dirname(__file__)
  
    fn = os.path.join(fileloc, 'test_data', *path)

    return fn

def assertDictLike(d1, d2, *args, **kwargs):
    yaml.Dumper.ignore_aliases = lambda *args : True
    d1str = yaml.dump(d1, default_flow_style=False)
    d2str = yaml.dump(d2, default_flow_style=False)

    d1str = d1str.format(*args, **kwargs)
    # print(d1str, d2str)
    d1l = yaml.load(d1str)
    d2l = yaml.load(d2str)
    assertEqual(d1l,d2l) 
# From https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python/24176022#24176022
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def dependency_generator(wf_name):
        if 'mi' in wf_name or 'mo' in wf_name:
            return {
                'step1/output' : 'output.txt',
                'step2/output' : 'output.txt',
                'step3/output' : 'output.txt'
            }
        else:
            return {}    
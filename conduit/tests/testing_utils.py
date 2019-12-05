import yaml
import os
def load_data(filename):
    fn = resolve_filename(filename)
    with open(fn) as fp:
        test_data = yaml.load(fp)
    return test_data
def resolve_filename(filename):
    fileloc = os.path.dirname(__file__)
    fn = os.path.join(fileloc, 'test_data', filename)
    return fn
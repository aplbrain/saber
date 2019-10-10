import yaml
def load_test_data(filename):
    fileloc = os.path.dirname(__file__)
    fn = os.path.join(fileloc, 'test_data', filename)
    with open(fn) as fp:
        test_data = yaml.load(fp)
    return test_data
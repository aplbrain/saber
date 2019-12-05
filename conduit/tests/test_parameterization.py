
import unittest
import yaml
import json
import os
import itertools
import numpy as np
from conduit.utils.parameterization import parameterize
from conduit.tests.testing_utils import load_data
class TestParameterization(unittest.TestCase):
    def setUp(self):
        self._test_data = load_data('test_parameterization.yml')
        
    def test_parameterize_single(self):
        data = self._test_data['metaparam1']
        data = {"metaparam1" : data}
        p = parameterize(data)
        expected_dict_format = {
            "step1" : {
                "param1" : "{a}"
            },
            "step2" : {
                "param1" : "{a}"
            },
            "step3" : {
                "param1" : "{a}"
            }
        }
        for i,step in enumerate(p):
            self.assertDictLike(expected_dict_format, step, a=0.1*i)
    def test_parameterize_multiple(self):
        data = {
            "metaparam1" : self._test_data['metaparam1'],
            "metaparam2" : self._test_data['metaparam2'],
        }
        p = parameterize(data)
        expected_dict_format = {
            "step1" : {
                "param1" : "{a}",
                "param2" : "{b}"
            },
            "step2" : {
                "param1" : "{a}",
                
            },
            "step3" : {
                "param1" : "{a}",
                
            }
        }
        vals = list(itertools.product(np.arange(0.0, 1, 0.1),np.arange(0.0, 0.2, 0.1)))
        self.assertEqual(len(p), len(vals))
        for step,(a,b) in zip(p,vals):

            self.assertDictLike(expected_dict_format,step, a=a, b=b)


    def assertDictLike(self, d1, d2, *args, **kwargs):
        yaml.Dumper.ignore_aliases = lambda *args : True
        d1str = yaml.dump(d1, default_flow_style=False)
        d2str = yaml.dump(d2, default_flow_style=False)

        d1str = d1str.format(*args, **kwargs)
        # print(d1str, d2str)
        d1l = yaml.load(d1str)
        d2l = yaml.load(d2str)
        self.assertEqual(d1l,d2l) 
        
if __name__ == "__main__":
    unittest.main()
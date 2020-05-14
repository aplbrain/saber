import unittest
from unittest.mock import MagicMock, patch
import datajoint as dj

# Wait until refactor here
# from conduit.utils.datajoint_hook import *
from conduit.utils.datajoint_hook import handle_key, DatajointHook, Workflow, JobMetadata
from conduit.tests.testing_utils import load_data, resolve_filename, WF_PREFIXES
import yaml

class TestHandleKey(unittest.TestCase):
    def test_handle_key(self):
        valid_test_keys = [
            '_SABER_key',
            '_saber_KEY',
            '_SABER_KEY',
            '_saber_key_1',
            '_saber_bucket',
            '_SaBeR_BuCkEt'
        ]
        invalid_test_keys = [
            
            'saberkey',
            'key_saber_',
            'saber_key',
            
            
            
        ]
        failure_test_keys = [
            'saber key is not this',
            '_this_is_not_a_saber_key',
            '1key',
            '*notakey',
            "Robert '); DROP TABLE Students; --"
        ]
        non_str_test_keys = [
            1,
            65.2,
          
            self
        ]
        for key in valid_test_keys:
            self.assertFalse(handle_key(key), msg=f'{key} failed')
        for key in invalid_test_keys:
            self.assertEquals(handle_key(key), key, msg=f'{key} failed')
        for key in failure_test_keys:
            with self.assertRaises(ValueError):
                handle_key(key)
        for key in non_str_test_keys:
            with self.assertRaises(AssertionError):
                handle_key(key)
class TestDatajointHook(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock(spec=dj.Connection)

        self.dj_conn_patch = patch('conduit.utils.datajoint_hook.dj.conn', return_value=self.mock_conn)
        self.dj_schema_patch = patch('conduit.utils.datajoint_hook.dj.schema')


        self.dj_conn_class = self.dj_conn_patch.start()
        self.dj_conn_mock = self.dj_schema_patch.start()
        self.dj_hook = DatajointHook(classdef=Workflow)
        self.local_wfs = {}
        for pre in WF_PREFIXES:
            self.local_wfs[pre] = load_data(resolve_filename('local_workflows',f'{pre}_workflow.cwl'))
        self.test_class_defs = load_data(resolve_filename('local_workflows', 'wf_class_defs.yml'))
    def tearDown(self):
        self.dj_conn_patch.stop()
        self.dj_conn_mock.stop()
       
    def test_create_definition(self):
        cls_defs = {}
        
        for key, wf in self.local_wfs.items():
            try:
                cls = self.dj_hook.create_definition(wf['inputs'],key)
                cls_defs[key] = cls.definition
            except AttributeError as e:
                cls_defs[key] = None
        self.assertDictEqual(self.test_class_defs, cls_defs)
    def test_create_table(self):
        for key, defn in self.test_class_defs.items():
            cls_def = type("{}Params".format(key.title()), (dj.Manual,), dict(definition=defn))
            self.dj_hook.create_table(conn=self.dj_hook.get_conn(), classdef=cls_def)
            self.dj_conn_mock.assert_called_with(schema_name='airflow', connection=self.mock_conn, context=self.dj_hook.context)
    
    def test_insert1(self):
        table_mock = MagicMock(spec=dj.Manual)
        with patch.object(self.dj_hook,'create_table', return_value=table_mock) as ct_mock:
            test_row = dict(
                key1 = 'key1',
                key2 = 4.2,
                key3 = 1,
   
            )
            fake_classdef = MagicMock(spec=dj.Manual)
            self.dj_hook.insert1(test_row, classdef=fake_classdef, skip_duplicates=True)
            ct_mock.assert_called_with(self.mock_conn, classdef=fake_classdef)
            table_mock.insert1.assert_called_with(test_row, skip_duplicates=True)

            self.dj_hook.insert1(test_row, classdef=fake_classdef, skip_duplicates=False)
            ct_mock.assert_called_with(self.mock_conn, classdef=fake_classdef)
            table_mock.insert1.assert_called_with(test_row, skip_duplicates=False)
    
    def test_update(self):
        table_mock = MagicMock(spec=dj.Manual)
        with patch.object(self.dj_hook,'create_table', return_value=table_mock) as ct_mock:
            primary_keys = MagicMock(spec=dict)
            test_row = dict(
                key1 = 'key1',
                key2 = 4.2,
                key3 = 1,
   
            )
            fake_classdef = MagicMock(spec=dj.Manual)
            self.dj_hook.update(test_row, classdef=fake_classdef, primary_keys=primary_keys)
            ct_mock.assert_called_with(self.mock_conn, classdef=fake_classdef)
            table_mock.insert1.assert_called_with(test_row, skip_duplicates=False)

            
            table_mock.insert1 = MagicMock(side_effect=dj.DuplicateError())

            
            with patch('conduit.utils.datajoint_hook.dj.config'):
                with self.assertRaises(dj.DuplicateError):
                    self.dj_hook.update(test_row, classdef=fake_classdef)
                    ct_mock.assert_called_with(self.mock_conn, classdef=fake_classdef)
                    table_mock.insert1.assert_called_with(test_row, skip_duplicates=False)
                    table_mock.__and__.assert_called_with(primary_keys)
                    table_mock.__and__.return_value.delete.assert_called()
    
    
    def test_query(self):
        
        with patch.object(self.dj_hook,'create_table', side_effect=lambda conn,classdef: classdef) as ct_mock:
            
            fake_classdef = MagicMock(spec=dj.Manual)
            self.dj_hook.query(classdef=fake_classdef)
            fake_classdef.__mul__.assert_called_with(JobMetadata)
            fake_classdef.__mul__.return_value.fetch.assert_called_with(as_dict=True)
                    
        
    

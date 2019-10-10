import unittest
from conduit.utils.command_list import generate_command_list, generate_io_strings, sub_params
import yaml

class TestCommandlist(unittest.TestCase):
    # TODO needs to be class
    
    def setUp(self):
        pass
    def test_generate_command_list(self):
        # Test cases:
        # 1. Single input, single output (SISO) tool
        # 2. Multi input, multi output (MIMO) tool
        # 3. MIMO tool with local
        # 4. MIMO tool with iteration parameters
        # 5. MIMO tool with no file path
        # 6. MIMO tool with file path
        pass
    def test_sub_params(self):
        # Test cases:
        # 1. Single input
        # 2. Multi input
        # 3. Edge case
        pass
    def test_generate_io_strings(self):
        # Test cases:
        # 1. Empty input
        # 2. Single input
        # 3. Multi input
        # 4. Edge case
        pass
    
    
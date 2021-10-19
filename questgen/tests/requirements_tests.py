# coding: utf-8
import unittest

from unittest import mock

from questgen import requirements


class TestRequirement(requirements.Requirement):
    attr_1 = requirements.RequirementAttribute()
    attr_2 = requirements.RequirementAttribute()



class RequirementsTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_interpreter_check_method(self):
        self.assertTrue(hasattr(TestRequirement, '_interpreter_check_method'))

    def test_interpreter_satisfy_method(self):
        self.assertTrue(hasattr(TestRequirement, '_interpreter_satisfy_method'))

    def test_check(self):
        interpreter = mock.Mock()
        requirement = TestRequirement(attr_1=1, attr_2=666)
        requirement.check(interpreter)
        self.assertEqual(interpreter.check_test_requirement.call_args_list, [mock.call(requirement=requirement)])

    def test_satisfy(self):
        interpreter = mock.Mock()
        requirement = TestRequirement(attr_1=1, attr_2=666)
        requirement.satisfy(interpreter)
        self.assertEqual(interpreter.satisfy_test_requirement.call_args_list, [mock.call(requirement=requirement)])

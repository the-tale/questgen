# coding: utf-8
import unittest

from unittest import mock

from questgen import actions


class TestAction(actions.Action):
    attr_1 = actions.ActionAttribute()
    attr_2 = actions.ActionAttribute()



class ActionsTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_interpreter_do_method(self):
        self.assertTrue(hasattr(TestAction, '_interpreter_do_method'))


    def test_do(self):
        interpreter = mock.Mock()
        action = TestAction(attr_1=1, attr_2=666)
        action.do(interpreter)
        self.assertEqual(interpreter.do_test_action.call_args_list, [mock.call(action=action)])

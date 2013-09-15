# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.machine import Machine
from questgen import exceptions
from questgen.facts import Place, Pointer, Start, Finish, State, Jump


class MachineTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        self.start = Start()
        self.state_1 = State(uid='state_1')
        self.state_2 = State(uid='state_2')
        self.finish_1 = Finish(uid='finish_1')

        self.kb += [ self.start, self.state_1, self.state_2, self.finish_1]

        self.machine = Machine(knowledge_base=self.kb)

    def test_get_pointer(self):
        self.assertEqual(list(self.kb.filter(Pointer)), [])
        pointer = self.machine.get_pointer()
        self.assertEqual(list(self.kb.filter(Pointer)), [pointer])

    def test_get_available_jumps__no_jumps(self):
        self.assertEqual(self.machine.get_available_jumps(self.start), [])

    def test_get_available_jumps__all_jumps(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertEqual(set(jump.uid for jump in self.machine.get_available_jumps(self.start)),
                         set([jump_1.uid, jump_2.uid]))

    def test_get_next_jump__no_jumps(self):
        self.assertRaises(exceptions.NoJumpsAvailableError,
                          self.machine.get_next_jump, self.start)

    def test_get_next_jump__all_jumps(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        jumps = set()

        for i in xrange(100):
            jumps.add(self.machine.get_next_jump(self.start).uid)

        self.assertEqual(jumps, set([jump_1.uid, jump_2.uid]))

    def test_can_do_step__no_pointer(self):
        self.assertEqual(list(self.kb.filter(Pointer)), [])
        self.assertTrue(self.machine.can_do_step())

    def test_can_do_step__requirement_failed(self):
        state_3 = State(uid='state_3', require=[Place(uid='unexisted_place')])
        jump_3 = Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.get_pointer()
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        self.assertFalse(self.machine.can_do_step())

    def test_can_do_step__success(self):
        state_3 = State(uid='state_3', require=[Start()])
        jump_3 = Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.get_pointer()
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        self.assertTrue(self.machine.can_do_step())


    def test_do_step__no_pointer(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertEqual(list(self.kb.filter(Pointer)), [])
        self.machine.step()
        self.assertEqual(len(list(self.kb.filter(Pointer))), 1)
        pointer = self.machine.get_pointer()
        self.assertEqual(pointer.state, self.start.uid)
        self.assertTrue(pointer.jump in [jump_1.uid, jump_2.uid])


    def test_do_step__finish(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.kb += jump_1

        self.machine.step()
        self.machine.step()

        pointer = self.machine.get_pointer()
        self.assertEqual(pointer.state, self.finish_1.uid)
        self.assertEqual(pointer.jump, None)


    def test_do_step__next_state(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.machine.step()
        self.machine.step()

        pointer = self.machine.get_pointer()
        self.assertEqual(pointer.state, self.state_1.uid)
        self.assertEqual(pointer.jump, jump_2.uid)

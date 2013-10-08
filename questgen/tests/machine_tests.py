# coding: utf-8
import mock

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.machine import Machine
from questgen import exceptions
from questgen.facts import Place, Pointer, Start, Finish, State, Jump, Choice, Option, ChoicePath


class MachineTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        self.start = Start(uid='start', type='test', nesting=0)
        self.state_1 = State(uid='state_1')
        self.state_2 = State(uid='state_2')
        self.finish_1 = Finish(uid='finish_1', result=0, nesting=0)

        self.kb += [ self.start, self.state_1, self.state_2, self.finish_1]

        self.machine = Machine(knowledge_base=self.kb)

    def test_get_pointer(self):
        self.assertEqual(list(self.kb.filter(Pointer)), [])
        pointer = self.machine.pointer
        self.assertEqual(list(self.kb.filter(Pointer)), [pointer])

    def test_get_available_jumps__no_jumps(self):
        self.assertEqual(self.machine.get_available_jumps(self.start), [])

    def test_get_available_jumps__all_jumps(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertEqual(set(jump.uid for jump in self.machine.get_available_jumps(self.start)),
                         set([jump_1.uid, jump_2.uid]))

    def test_get_available_jumps__for_choice_state(self):
        choice = Choice(uid='choice')
        option_1 = Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1')
        option_2 = Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2')
        path = ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice, option_1, option_2, path)

        for i in xrange(100):
            self.assertEqual(self.machine.get_available_jumps(choice), [option_2])

    def test_get_next_jump__no_jumps(self):
        self.assertRaises(exceptions.NoJumpsAvailableError,
                          self.machine.get_next_jump, self.start)

    def test_get_next_jump__all_jumps(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        jumps = set()

        for i in xrange(100):
            jumps.add(self.machine.get_next_jump(self.start, single=False).uid)

        self.assertEqual(jumps, set([jump_1.uid, jump_2.uid]))

    def test_get_next_jump__require_one_jump__exception(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertRaises(exceptions.MoreThenOneJumpsAvailableError, self.machine.get_next_jump, self.start, single=True)

    def test_get_next_jump__require_one_jump(self):
        jump = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        self.kb += jump
        self.assertEqual(self.machine.get_next_jump(self.start, single=True).uid, jump.uid)

    def test_can_do_step__no_pointer(self):
        self.assertEqual(list(self.kb.filter(Pointer)), [])
        self.assertTrue(self.machine.can_do_step())

    def test_can_do_step__requirement_failed(self):
        state_3 = State(uid='state_3', require=[Place(uid='unexisted_place')])
        jump_3 = Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.pointer
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        self.assertFalse(self.machine.can_do_step())

    def test_can_do_step__success(self):
        state_3 = State(uid='state_3', require=[Start(uid='start', type='test', nesting=0)])
        jump_3 = Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.pointer
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        self.assertTrue(self.machine.can_do_step())


    def test_do_step__no_pointer(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine, 'on_state') as on_state:
            with mock.patch.object(self.machine, 'on_jump_start') as on_jump_start:
                with mock.patch.object(self.machine, 'on_jump_end') as on_jump_end:

                    calls_manager.attach_mock(on_state, 'on_state')
                    calls_manager.attach_mock(on_jump_start, 'on_jump_start')
                    calls_manager.attach_mock(on_jump_end, 'on_jump_end')

                    self.assertEqual(list(self.kb.filter(Pointer)), [])
                    self.machine.step()
                    self.assertEqual(len(list(self.kb.filter(Pointer))), 1)

                    self.assertEqual(calls_manager.mock_calls, [mock.call.on_state(state=self.start)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, None)


    def test_do_step__finish(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.kb += jump_1

        self.machine.step()
        self.machine.step()

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine, 'on_state') as on_state:
            with mock.patch.object(self.machine, 'on_jump_start') as on_jump_start:
                with mock.patch.object(self.machine, 'on_jump_end') as on_jump_end:

                    calls_manager.attach_mock(on_state, 'on_state')
                    calls_manager.attach_mock(on_jump_start, 'on_jump_start')
                    calls_manager.attach_mock(on_jump_end, 'on_jump_end')

                    self.machine.step()

                    self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_end(jump=jump_1),
                                                                mock.call.on_state(state=self.finish_1)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.finish_1.uid)
        self.assertEqual(pointer.jump, None)

    def test_do_step__step_after_finish(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.kb += jump_1

        self.machine.step()
        self.machine.step()
        self.machine.step()

        self.assertRaises(exceptions.NoJumpsFromLastStateError, self.machine.step)

    def test_do_step__next_jump(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.machine.step()

        calls_manager = mock.MagicMock()

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, None)

        with mock.patch.object(self.machine, 'on_state') as on_state:
            with mock.patch.object(self.machine, 'on_jump_start') as on_jump_start:
                with mock.patch.object(self.machine, 'on_jump_end') as on_jump_end:

                    calls_manager.attach_mock(on_state, 'on_state')
                    calls_manager.attach_mock(on_jump_start, 'on_jump_start')
                    calls_manager.attach_mock(on_jump_end, 'on_jump_end')

                    self.machine.step()

                    self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start(jump=jump_1)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, jump_1.uid)

    def test_do_step__next_state(self):
        jump_1 = Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.machine.step()
        self.machine.step()
        self.machine.step()

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.state_1.uid)
        self.assertEqual(pointer.jump, None)

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine, 'on_state') as on_state:
            with mock.patch.object(self.machine, 'on_jump_start') as on_jump_start:
                with mock.patch.object(self.machine, 'on_jump_end') as on_jump_end:

                    calls_manager.attach_mock(on_state, 'on_state')
                    calls_manager.attach_mock(on_jump_start, 'on_jump_start')
                    calls_manager.attach_mock(on_jump_end, 'on_jump_end')

                    self.machine.step()

                    self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start(jump=jump_2)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.state_1.uid)
        self.assertEqual(pointer.jump, jump_2.uid)

    def test_sync_pointer(self):
        choice = Choice(uid='choice')
        option_1 = Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1')
        option_2 = Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2')
        path = ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        pointer = Pointer(state=choice.uid, jump=option_1.uid)

        self.kb += (choice, option_1, option_2, path, pointer)

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine, 'on_state') as on_state:
            with mock.patch.object(self.machine, 'on_jump_start') as on_jump_start:
                with mock.patch.object(self.machine, 'on_jump_end') as on_jump_end:

                    calls_manager.attach_mock(on_state, 'on_state')
                    calls_manager.attach_mock(on_jump_start, 'on_jump_start')
                    calls_manager.attach_mock(on_jump_end, 'on_jump_end')

                    self.machine.sync_pointer()

                    self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start(jump=option_2)])

        self.assertEqual(self.machine.pointer.jump, option_2.uid)
        self.assertEqual(self.machine.pointer.state, choice.uid)

    def test_get_start_state(self):
        start_2 = Start(uid='s2', type='test', nesting=0)
        start_3 = Start(uid='start_3', type='test', nesting=0)


        self.kb += [ start_2,
                     start_3,
                     Jump(state_from=self.start.uid, state_to=start_2.uid),
                     Jump(state_from=start_3.uid, state_to=self.start.uid) ]

        self.assertEqual(self.machine.get_start_state().uid, start_3.uid)

    def test_get_nearest_choice__no_choice(self):
        self.kb += Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

    def test_get_nearest_choice__choice(self):
        choice = Choice(uid='choice')
        option_1 = Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1')
        option_2 = Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2')
        path = ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    Jump(state_from=self.start.uid, state_to=choice.uid)    )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_1.uid, option_2.uid]))
        self.assertEqual([p.uid for p in path_], [path.uid])

    def test_get_nearest_choice__2_choices(self):
        choice_1 = Choice(uid='choice_1')

        choice_2 = Choice(uid='choice_2')
        option_2_1 = Option(state_from=choice_2.uid, state_to=self.state_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=self.state_2.uid, type='opt_2_2')
        path_2 = ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)

        option_1_1 = Option(state_from=choice_1.uid, state_to=self.state_1.uid, type='opt_1_1')
        option_1_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_1_2')
        path_1 = ChoicePath(choice=choice_1.uid, option=option_1_2.uid, default=True)

        self.kb += (choice_1,
                    option_1_1,
                    option_1_2,
                    path_1,

                    choice_2,
                    option_2_1,
                    option_2_2,
                    path_2,
                    Jump(state_from=self.start.uid, state_to=choice_1.uid),
            )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice_1.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_1_1.uid, option_1_2.uid]))
        self.assertEqual([p.uid for p in path_], [path_1.uid])

    def test_get_nearest_choice__2_choices__second_choice(self):
        choice_1 = Choice(uid='choice_1')

        choice_2 = Choice(uid='choice_2')
        option_2_1 = Option(state_from=choice_2.uid, state_to=self.state_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=self.state_2.uid, type='opt_2_2')
        path_2 = ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)

        option_1_1 = Option(state_from=choice_1.uid, state_to=self.state_1.uid, type='opt_1_1')
        option_1_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_1_2')
        path_1 = ChoicePath(choice=choice_1.uid, option=option_1_2.uid, default=True)

        self.kb += (choice_1,
                    option_1_1,
                    option_1_2,
                    path_1,

                    choice_2,
                    option_2_1,
                    option_2_2,
                    path_2,
                    Jump(state_from=self.start.uid, state_to=choice_1.uid),

                    Pointer(state=choice_2.uid)
            )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice_2.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_2_1.uid, option_2_2.uid]))
        self.assertEqual([p.uid for p in path_], [path_2.uid])

    def test_get_nearest_choice__choice_after_finish(self):
        choice = Choice(uid='choice')
        option_1 = Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1')
        option_2 = Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2')
        path = ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    Jump(state_from=self.start.uid, state_to=self.finish_1.uid),
                    Jump(state_from=self.finish_1.uid, state_to=choice.uid))

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

    def test_get_nearest_choice__choice_after_start(self):
        choice = Choice(uid='choice')
        option_1 = Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1')
        option_2 = Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2')
        path = ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        start_2 = Start(uid='start_2', type='test', nesting=0)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    start_2,
                    Jump(state_from=self.start.uid, state_to=start_2.uid),
                    Jump(state_from=start_2.uid, state_to=choice.uid))

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

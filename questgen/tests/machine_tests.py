# coding: utf-8

import unittest

from unittest import mock

from questgen.knowledge_base import KnowledgeBase
from questgen.machine import Machine
from questgen import exceptions
from questgen import facts
from questgen import requirements
from questgen.tests.helpers import FakeInterpreter


class MachineTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        self.hero = facts.Hero(uid='hero')

        self.start = facts.Start(uid='start', type='test', nesting=0)
        self.state_1 = facts.State(uid='state_1')
        self.state_2 = facts.State(uid='state_2')
        self.finish_1 = facts.Finish(start='start', uid='finish_1', results={}, nesting=0)

        self.kb += [self.start, self.state_1, self.state_2, self.finish_1, self.hero]

        self.machine = Machine(knowledge_base=self.kb, interpreter=FakeInterpreter())

    def test_get_pointer(self):
        self.assertEqual(list(self.kb.filter(facts.Pointer)), [])
        pointer = self.machine.pointer
        self.assertEqual(list(self.kb.filter(facts.Pointer)), [pointer])

    def test_get_available_jumps__no_jumps(self):
        self.assertEqual(self.machine.get_available_jumps(self.start), [])

    def test_get_available_jumps__all_jumps(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertEqual(set(jump.uid for jump in self.machine.get_available_jumps(self.start)),
                         set([jump_1.uid, jump_2.uid]))

    def test_get_available_jumps__for_choice_state(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice, option_1, option_2, path)

        for i in range(100):
            self.assertEqual(self.machine.get_available_jumps(choice), [option_2])

    def test_get_available_jumps__for_question_state(self):
        condition = requirements.LocatedIn(object='object', place='place')

        question = facts.Question(uid='choice', condition=[condition])
        answer_1 = facts.Answer(state_from=question.uid, state_to=self.state_1.uid, condition=True)
        answer_2 = facts.Answer(state_from=question.uid, state_to=self.state_2.uid, condition=False)
        self.kb += (question, answer_1, answer_2)

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=False)):
            for i in range(100):
                self.assertEqual(self.machine.get_available_jumps(question), [answer_2])

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=True)):
            for i in range(100):
                self.assertEqual(self.machine.get_available_jumps(question), [answer_1])

    def test_get_next_jump__no_jumps(self):
        self.assertRaises(exceptions.NoJumpsAvailableError,
                          self.machine.get_next_jump, self.start)

    def test_get_next_jump__all_jumps(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        jumps = set()

        for i in range(100):
            jumps.add(self.machine.get_next_jump(self.start, single=False).uid)

        self.assertEqual(jumps, set([jump_1.uid, jump_2.uid]))

    def test_get_next_jump__require_one_jump__exception(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.start.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.assertRaises(exceptions.MoreThenOneJumpsAvailableError, self.machine.get_next_jump, self.start, single=True)

    def test_get_next_jump__require_one_jump(self):
        jump = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        self.kb += jump
        self.assertEqual(self.machine.get_next_jump(self.start, single=True).uid, jump.uid)

    def test_can_do_step__no_pointer(self):
        self.assertEqual(list(self.kb.filter(facts.Pointer)), [])
        self.assertTrue(self.machine.can_do_step())

    @mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_is_alive=False))
    def test_can_do_step__requirement_failed(self):
        state_3 = facts.State(uid='state_3', require=[requirements.IsAlive(object='hero')])
        jump_3 = facts.Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.pointer
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        self.assertFalse(self.machine.can_do_step())

    def test_can_do_step__success(self):
        state_3 = facts.State(uid='state_3', require=[requirements.IsAlive(object='hero')])
        jump_3 = facts.Jump(state_from=self.start.uid, state_to=state_3.uid)
        self.kb += [ state_3, jump_3]

        pointer = self.machine.pointer
        self.kb -= pointer
        self.kb += pointer.change(state=self.start.uid, jump=jump_3.uid)

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_is_alive=True)):
            self.assertTrue(self.machine.can_do_step())


    def test_do_step__no_pointer(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine.interpreter, 'on_state__before_actions') as on_state__before_actions:
            with mock.patch.object(self.machine.interpreter, 'on_state__after_actions') as on_state__after_actions:
                with mock.patch.object(self.machine.interpreter, 'on_jump_start__before_actions') as on_jump_start__before_actions:
                    with mock.patch.object(self.machine.interpreter, 'on_jump_start__after_actions') as on_jump_start__after_actions:
                        with mock.patch.object(self.machine.interpreter, 'on_jump_end__before_actions') as on_jump_end__before_actions:
                            with mock.patch.object(self.machine.interpreter, 'on_jump_end__after_actions') as on_jump_end__after_actions:

                                calls_manager.attach_mock(on_state__before_actions, 'on_state__before_actions')
                                calls_manager.attach_mock(on_state__after_actions, 'on_state__after_actions')
                                calls_manager.attach_mock(on_jump_start__before_actions, 'on_jump_start__before_actions')
                                calls_manager.attach_mock(on_jump_start__after_actions, 'on_jump_start__after_actions')
                                calls_manager.attach_mock(on_jump_end__before_actions, 'on_jump_end__before_actions')
                                calls_manager.attach_mock(on_jump_end__after_actions, 'on_jump_end__after_actions')

                                self.assertEqual(list(self.kb.filter(facts.Pointer)), [])
                                self.machine.step()
                                self.assertEqual(len(list(self.kb.filter(facts.Pointer))), 1)

                                self.assertEqual(calls_manager.mock_calls, [mock.call.on_state__before_actions(state=self.start),
                                                                            mock.call.on_state__after_actions(state=self.start)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, None)


    def test_do_step__finish(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.kb += jump_1

        self.machine.step()
        self.machine.step()

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine.interpreter, 'on_state__before_actions') as on_state__before_actions:
            with mock.patch.object(self.machine.interpreter, 'on_state__after_actions') as on_state__after_actions:
                with mock.patch.object(self.machine.interpreter, 'on_jump_start__before_actions') as on_jump_start__before_actions:
                    with mock.patch.object(self.machine.interpreter, 'on_jump_start__after_actions') as on_jump_start__after_actions:
                        with mock.patch.object(self.machine.interpreter, 'on_jump_end__before_actions') as on_jump_end__before_actions:
                            with mock.patch.object(self.machine.interpreter, 'on_jump_end__after_actions') as on_jump_end__after_actions:

                                calls_manager.attach_mock(on_state__before_actions, 'on_state__before_actions')
                                calls_manager.attach_mock(on_state__after_actions, 'on_state__after_actions')
                                calls_manager.attach_mock(on_jump_start__before_actions, 'on_jump_start__before_actions')
                                calls_manager.attach_mock(on_jump_start__after_actions, 'on_jump_start__after_actions')
                                calls_manager.attach_mock(on_jump_end__before_actions, 'on_jump_end__before_actions')
                                calls_manager.attach_mock(on_jump_end__after_actions, 'on_jump_end__after_actions')

                                self.machine.step()

                                self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_end__before_actions(jump=jump_1),
                                                                            mock.call.on_jump_end__after_actions(jump=jump_1),
                                                                            mock.call.on_state__before_actions(state=self.finish_1),
                                                                            mock.call.on_state__after_actions(state=self.finish_1)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.finish_1.uid)
        self.assertEqual(pointer.jump, None)

    def test_do_step__step_after_finish(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.kb += jump_1

        self.machine.step()
        self.machine.step()
        self.machine.step()

        self.assertRaises(exceptions.NoJumpsFromLastStateError, self.machine.step)

    def test_do_step__next_jump(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.machine.step()

        calls_manager = mock.MagicMock()

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, None)

        with mock.patch.object(self.machine.interpreter, 'on_state__before_actions') as on_state__before_actions:
            with mock.patch.object(self.machine.interpreter, 'on_state__after_actions') as on_state__after_actions:
                with mock.patch.object(self.machine.interpreter, 'on_jump_start__before_actions') as on_jump_start__before_actions:
                    with mock.patch.object(self.machine.interpreter, 'on_jump_start__after_actions') as on_jump_start__after_actions:
                        with mock.patch.object(self.machine.interpreter, 'on_jump_end__before_actions') as on_jump_end__before_actions:
                            with mock.patch.object(self.machine.interpreter, 'on_jump_end__after_actions') as on_jump_end__after_actions:

                                calls_manager.attach_mock(on_state__before_actions, 'on_state__before_actions')
                                calls_manager.attach_mock(on_state__after_actions, 'on_state__after_actions')
                                calls_manager.attach_mock(on_jump_start__before_actions, 'on_jump_start__before_actions')
                                calls_manager.attach_mock(on_jump_start__after_actions, 'on_jump_start__after_actions')
                                calls_manager.attach_mock(on_jump_end__before_actions, 'on_jump_end__before_actions')
                                calls_manager.attach_mock(on_jump_end__after_actions, 'on_jump_end__after_actions')

                                self.machine.step()

                                self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start__before_actions(jump=jump_1),
                                                                            mock.call.on_jump_start__after_actions(jump=jump_1)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.start.uid)
        self.assertEqual(pointer.jump, jump_1.uid)

    def test_do_step__next_state(self):
        jump_1 = facts.Jump(state_from=self.start.uid, state_to=self.state_1.uid)
        jump_2 = facts.Jump(state_from=self.state_1.uid, state_to=self.state_2.uid)
        self.kb += [jump_1, jump_2]

        self.machine.step()
        self.machine.step()
        self.machine.step()

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.state_1.uid)
        self.assertEqual(pointer.jump, None)

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine.interpreter, 'on_state__before_actions') as on_state__before_actions:
            with mock.patch.object(self.machine.interpreter, 'on_state__after_actions') as on_state__after_actions:
                with mock.patch.object(self.machine.interpreter, 'on_jump_start__before_actions') as on_jump_start__before_actions:
                    with mock.patch.object(self.machine.interpreter, 'on_jump_start__after_actions') as on_jump_start__after_actions:
                        with mock.patch.object(self.machine.interpreter, 'on_jump_end__before_actions') as on_jump_end__before_actions:
                            with mock.patch.object(self.machine.interpreter, 'on_jump_end__after_actions') as on_jump_end__after_actions:

                                calls_manager.attach_mock(on_state__before_actions, 'on_state__before_actions')
                                calls_manager.attach_mock(on_state__after_actions, 'on_state__after_actions')
                                calls_manager.attach_mock(on_jump_start__before_actions, 'on_jump_start__before_actions')
                                calls_manager.attach_mock(on_jump_start__after_actions, 'on_jump_start__after_actions')
                                calls_manager.attach_mock(on_jump_end__before_actions, 'on_jump_end__before_actions')
                                calls_manager.attach_mock(on_jump_end__after_actions, 'on_jump_end__after_actions')

                                self.machine.step()

                                self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start__before_actions(jump=jump_2),
                                                                            mock.call.on_jump_start__after_actions(jump=jump_2)])

        pointer = self.machine.pointer
        self.assertEqual(pointer.state, self.state_1.uid)
        self.assertEqual(pointer.jump, jump_2.uid)

    def test_sync_pointer(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        pointer = facts.Pointer(state=choice.uid, jump=option_1.uid)

        self.kb += (choice, option_1, option_2, path, pointer)

        calls_manager = mock.MagicMock()

        with mock.patch.object(self.machine.interpreter, 'on_state__before_actions') as on_state__before_actions:
            with mock.patch.object(self.machine.interpreter, 'on_state__after_actions') as on_state__after_actions:
                with mock.patch.object(self.machine.interpreter, 'on_jump_start__before_actions') as on_jump_start__before_actions:
                    with mock.patch.object(self.machine.interpreter, 'on_jump_start__after_actions') as on_jump_start__after_actions:
                        with mock.patch.object(self.machine.interpreter, 'on_jump_end__before_actions') as on_jump_end__before_actions:
                            with mock.patch.object(self.machine.interpreter, 'on_jump_end__after_actions') as on_jump_end__after_actions:

                                calls_manager.attach_mock(on_state__before_actions, 'on_state__before_actions')
                                calls_manager.attach_mock(on_state__after_actions, 'on_state__after_actions')
                                calls_manager.attach_mock(on_jump_start__before_actions, 'on_jump_start__before_actions')
                                calls_manager.attach_mock(on_jump_start__after_actions, 'on_jump_start__after_actions')
                                calls_manager.attach_mock(on_jump_end__before_actions, 'on_jump_end__before_actions')
                                calls_manager.attach_mock(on_jump_end__after_actions, 'on_jump_end__after_actions')

                                self.machine.sync_pointer()

                                self.assertEqual(calls_manager.mock_calls, [mock.call.on_jump_start__before_actions(jump=option_2),
                                                                            mock.call.on_jump_start__after_actions(jump=option_2)])

        self.assertEqual(self.machine.pointer.jump, option_2.uid)
        self.assertEqual(self.machine.pointer.state, choice.uid)

    def test_get_start_state(self):
        start_2 = facts.Start(uid='s2', type='test', nesting=0)
        start_3 = facts.Start(uid='start_3', type='test', nesting=0)


        self.kb += [ start_2,
                     start_3,
                     facts.Jump(state_from=self.start.uid, state_to=start_2.uid),
                     facts.Jump(state_from=start_3.uid, state_to=self.start.uid) ]

        self.assertEqual(self.machine.get_start_state().uid, start_3.uid)

    def test_get_nearest_choice__no_choice(self):
        self.kb += facts.Jump(state_from=self.start.uid, state_to=self.finish_1.uid)
        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

    def test_get_nearest_choice__choice(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    facts.Jump(state_from=self.start.uid, state_to=choice.uid)    )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_1.uid, option_2.uid]))
        self.assertEqual([p.uid for p in path_], [path.uid])

    def test_get_nearest_choice__2_choices(self):
        choice_1 = facts.Choice(uid='choice_1')

        choice_2 = facts.Choice(uid='choice_2')
        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=self.state_1.uid, type='opt_2_1', markers=())
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=self.state_2.uid, type='opt_2_2', markers=())
        path_2 = facts.ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)

        option_1_1 = facts.Option(state_from=choice_1.uid, state_to=self.state_1.uid, type='opt_1_1', markers=())
        option_1_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_1_2', markers=())
        path_1 = facts.ChoicePath(choice=choice_1.uid, option=option_1_2.uid, default=True)

        self.kb += (choice_1,
                    option_1_1,
                    option_1_2,
                    path_1,

                    choice_2,
                    option_2_1,
                    option_2_2,
                    path_2,
                    facts.Jump(state_from=self.start.uid, state_to=choice_1.uid),
            )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice_1.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_1_1.uid, option_1_2.uid]))
        self.assertEqual([p.uid for p in path_], [path_1.uid])

    def test_get_nearest_choice__2_choices__second_choice(self):
        choice_1 = facts.Choice(uid='choice_1')

        choice_2 = facts.Choice(uid='choice_2')
        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=self.state_1.uid, type='opt_2_1', markers=())
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=self.state_2.uid, type='opt_2_2', markers=())
        path_2 = facts.ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)

        option_1_1 = facts.Option(state_from=choice_1.uid, state_to=self.state_1.uid, type='opt_1_1', markers=())
        option_1_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_1_2', markers=())
        path_1 = facts.ChoicePath(choice=choice_1.uid, option=option_1_2.uid, default=True)

        self.kb += (choice_1,
                    option_1_1,
                    option_1_2,
                    path_1,

                    choice_2,
                    option_2_1,
                    option_2_2,
                    path_2,
                    facts.Jump(state_from=self.start.uid, state_to=choice_1.uid),

                    facts.Pointer(state=choice_2.uid)
            )

        choice_, options_, path_ = self.machine.get_nearest_choice()
        self.assertEqual(choice_.uid, choice_2.uid)
        self.assertEqual(set(o.uid for o in options_), set([option_2_1.uid, option_2_2.uid]))
        self.assertEqual([p.uid for p in path_], [path_2.uid])

    def test_get_nearest_choice__choice_after_finish(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    facts.Jump(state_from=self.start.uid, state_to=self.finish_1.uid),
                    facts.Jump(state_from=self.finish_1.uid, state_to=choice.uid))

        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

    def test_get_nearest_choice__choice_after_question(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)

        question = facts.Question(uid='question', condition=())

        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    question,
                    facts.Jump(state_from=self.start.uid, state_to=question.uid),
                    facts.Jump(state_from=question.uid, state_to=choice.uid))

        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))

    def test_get_nearest_choice__choice_after_start(self):
        choice = facts.Choice(uid='choice')
        option_1 = facts.Option(state_from=choice.uid, state_to=self.state_1.uid, type='opt_1', markers=())
        option_2 = facts.Option(state_from=choice.uid, state_to=self.state_2.uid, type='opt_2', markers=())
        path = facts.ChoicePath(choice=choice.uid, option=option_2.uid, default=True)
        start_2 = facts.Start(uid='start_2', type='test', nesting=0)
        self.kb += (choice,
                    option_1,
                    option_2,
                    path,
                    start_2,
                    facts.Jump(state_from=self.start.uid, state_to=start_2.uid),
                    facts.Jump(state_from=start_2.uid, state_to=choice.uid))

        self.assertEqual(self.machine.get_nearest_choice(), (None, None, None))


    @mock.patch('questgen.machine.Machine.can_do_step', lambda self: True)
    def test_do_step__step_done(self):
        with mock.patch('questgen.machine.Machine.step') as step:
            self.assertTrue(self.machine.do_step())

        self.assertEqual(step.call_args_list, [mock.call()])

    @mock.patch('questgen.machine.Machine.can_do_step', lambda self: False)
    @mock.patch('questgen.machine.Machine.is_processed', True)
    def test_do_step__quest_processed(self):
        with mock.patch('questgen.machine.Machine.step') as step:
            self.assertFalse(self.machine.do_step())

        self.assertEqual(step.call_args_list, [])

    @mock.patch('questgen.machine.Machine.can_do_step', lambda self: False)
    @mock.patch('questgen.machine.Machine.is_processed', False)
    @mock.patch('questgen.machine.Machine.next_state', 'next-state')
    def test_do_step__satisfy_requirements(self):
        with mock.patch('questgen.machine.Machine.step') as step:
            with mock.patch('questgen.machine.Machine.satisfy_requirements') as satisfy_requirements:
                self.assertTrue(self.machine.do_step())

        self.assertEqual(step.call_args_list, [])
        self.assertEqual(satisfy_requirements.call_args_list, [mock.call('next-state')])

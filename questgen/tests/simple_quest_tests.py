# coding: utf-8

import unittest

from unittest import mock

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Place, Person
from questgen.facts import Start, Finish, State, Jump
from questgen.facts import LocatedIn
from questgen.facts import Hero, Pointer
from questgen import restrictions
from questgen import machine
from questgen import requirements
from questgen.tests.helpers import FakeInterpreter


class SimpleQuestTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        # world
        self.kb += [ Place(uid='place_from'),
                     Person(uid='person_from'),
                     Place(uid='place_thought'),
                     Place(uid='place_to'),
                     Person(uid='person_to'),
                     LocatedIn(object='person_from', place='place_from'),
                     LocatedIn(object='person_to', place='place_to')]

        # quest
        self.kb += [ Start(uid='start',
                           nesting=0,
                           type='simple_test',
                           require=(requirements.LocatedIn(object='person_from', place='place_from'),
                                    requirements.LocatedIn(object='person_to', place='place_to'),
                                    requirements.LocatedIn(object='hero', place='place_from'))),

                     State(uid='st_throught_place',
                           require=(requirements.LocatedIn(object='hero', place='place_thought'),)),

                     Finish(uid='st_finish',
                            start='start',
                            results={},
                            nesting=0,
                            require=(requirements.LocatedIn(object='hero', place='place_to'),)),

                     Jump(state_from='start', state_to='st_throught_place'),
                     Jump(state_from='st_throught_place', state_to='st_finish') ]

        self.kb += [ Hero(uid='hero') ]

        self.kb.validate_consistency([restrictions.SingleStartStateWithNoEnters(),
                                      restrictions.FinishStateExists(),
                                      restrictions.AllStatesHasJumps(),
                                      restrictions.SingleLocationForObject(),
                                      restrictions.ReferencesIntegrity(),
                                      restrictions.ConnectedStateJumpGraph(),
                                      restrictions.NoCirclesInStateJumpGraph(),
                                      restrictions.MultipleJumpsFromNormalState(),
                                      restrictions.ChoicesConsistency()])

        self.machine = machine.Machine(knowledge_base=self.kb, interpreter=FakeInterpreter())

    def test_initialized(self):
        pass

    def test_full_story_forced(self):
        self.machine.step()
        self.assertEqual(self.machine.pointer, Pointer(state='start'))

        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))

        self.machine.step()
        self.assertEqual(self.machine.pointer, Pointer(state='st_throught_place'))

        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_finish', jump=None))


    def test_full_story_real(self):
        # no move, since hero not in right place
        self.assertEqual(self.machine.pointer, Pointer(state=None, jump=None) )

        def check_located_in_place_from(requirement):
            return requirement.place == 'place_from'

        def check_located_in_place_to(requirement):
            return requirement.place == 'place_to'

        def check_located_in_place_thought(requirement):
            return requirement.place == 'place_thought'

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_from)):
            self.machine.step_until_can()

        self.assertEqual(self.machine.pointer, Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid) )

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_from)):
            self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))

        # no move, since hero not in right place
        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_from)):
            self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_thought)):
            self.machine.step_until_can()

        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        # no move, since hero not in right place
        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_thought)):
            self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        with mock.patch('questgen.machine.Machine.interpreter', FakeInterpreter(check_located_in=check_located_in_place_to)):
            self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_finish', jump=None))

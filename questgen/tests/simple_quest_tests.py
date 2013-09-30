# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Place, Person
from questgen.facts import Start, Finish, State, Jump
from questgen.facts import LocatedIn
from questgen.facts import Hero, Pointer
from questgen import restrictions
from questgen import machine


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
                           type='simple_test',
                           require=(LocatedIn(object='person_from', place='place_from'),
                                    LocatedIn(object='person_to', place='place_to'),
                                    LocatedIn(object='hero', place='place_from'))),

                     State(uid='st_throught_place',
                           require=(LocatedIn(object='hero', place='place_thought'),)),

                     Finish(uid='st_finish',
                            type='finish',
                            require=(LocatedIn(object='hero', place='place_to'),)),

                     Jump(state_from='start', state_to='st_throught_place'),
                     Jump(state_from='st_throught_place', state_to='st_finish') ]

        self.kb += [ Hero(uid='hero') ]

        self.kb.validate_consistency([ restrictions.SingleStartState(),
                                       restrictions.NoJumpsFromFinish(),
                                       restrictions.SingleLocationForObject(),
                                       restrictions.ReferencesIntegrity(),
                                       restrictions.ConnectedStateJumpGraph(),
                                       restrictions.NoCirclesInStateJumpGraph() ])

        self.machine = machine.Machine(knowledge_base=self.kb)

    def test_initialized(self):
        pass

    def test_full_story_forced(self):
        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))
        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        self.machine.step()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_finish', jump=None))


    def test_full_story_real(self):
        # no move, since hero not in right place
        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer, Pointer(state=None, jump=None) )

        self.kb += LocatedIn(object='hero', place='place_from')

        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))

        # no move, since hero not in right place
        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='start', jump=Jump(state_from='start', state_to='st_throught_place').uid))

        LocatedIn.relocate(self.kb, 'hero', 'place_thought')
        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        # no move, since hero not in right place
        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_throught_place',
                                 jump=Jump(state_from='st_throught_place', state_to='st_finish').uid))

        LocatedIn.relocate(self.kb, 'hero', 'place_to')
        self.machine.step_until_can()
        self.assertEqual(self.machine.pointer,
                         Pointer(state='st_finish', jump=None))

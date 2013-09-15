# coding: utf-8

import unittest

from questgen import exceptions
from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Start, State, Jump, Finish, Event
from questgen.transformators import activate_events, remove_broken_states


class TransformatorsTestsBase(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

    def check_in_knowledge_base(self, knowlege_base, facts):
        for fact in facts:
            self.assertTrue(fact.uid in knowlege_base)

    def check_not_in_knowledge_base(self, knowlege_base, facts):
        for fact in facts:
            self.assertFalse(fact.uid in knowlege_base)


class ActivateEventsTests(TransformatorsTestsBase):

    def setUp(self):
        super(ActivateEventsTests, self).setUp()

    def test_no_events(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts
        activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_no_tag(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish'),
                  Event(tag='event_tag') ]
        self.kb += facts
        self.assertRaises(exceptions.NoTaggedEventMembersError, activate_events, self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_simple_tagged_jump(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish', tags=('event_tag', )),
                  Event(tag='event_tag') ]
        self.kb += facts
        activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_multiple_tagged_jump(self):
        facts = [ Start(),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Event(tag='event_tag') ]
        self.kb += facts

        jump_1 = Jump(state_from=Start.UID, state_to='st_finish_1', tags=('event_tag', ))
        jump_2 = Jump(state_from=Start.UID, state_to='st_finish_2', tags=('event_tag', ))

        self.kb += (jump_1, jump_2)

        activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertTrue( (jump_1.uid in self.kb and jump_2.uid not in self.kb) or
                         (jump_2.uid in self.kb and jump_1.uid not in self.kb) )

    def test_multiple_events_jump_marked_for_multiple_events(self):
        facts = [ Start(),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Event(tag='event_tag'),
                  Event(tag='event_2_tag')]
        self.kb += facts

        jump_1 = Jump(state_from=Start.UID, state_to='st_finish_1', tags=('event_tag', 'event_2_tag'))
        jump_2 = Jump(state_from=Start.UID, state_to='st_finish_2', tags=('event_tag',))

        self.kb += (jump_1, jump_2)

        self.assertRaises(exceptions.MoreThenOneEventTagError, activate_events, self.kb)

    def test_multiple_events(self):
        facts = [ Start(),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Finish(uid='st_finish_3'),
                  Finish(uid='st_finish_4'),
                  Event(tag='event_tag'),
                  Event(tag='event_2_tag')]

        self.kb += facts

        jump_1 = Jump(state_from=Start.UID, state_to='st_finish_1', tags=('event_tag',))
        jump_2 = Jump(state_from=Start.UID, state_to='st_finish_2', tags=('event_tag',))
        jump_3 = Jump(state_from=Start.UID, state_to='st_finish_3', tags=('event_2_tag',))
        jump_4 = Jump(state_from=Start.UID, state_to='st_finish_4', tags=('event_2_tag',))

        self.kb += (jump_1, jump_2, jump_3, jump_4)

        activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertTrue( (jump_1.uid in self.kb and jump_2.uid not in self.kb) or
                         (jump_2.uid in self.kb and jump_1.uid not in self.kb) )
        self.assertTrue( (jump_3.uid in self.kb and jump_4.uid not in self.kb) or
                         (jump_4.uid in self.kb and jump_3.uid not in self.kb) )

    def test_tagged_not_jump(self):
        facts = [ Start(),
                  Finish(uid='st_finish', tags=('event_tag', )),
                  Jump(state_from=Start.UID, state_to='st_finish', tags=('event_tag', )),
                  Event(tag='event_tag') ]
        self.kb += facts
        self.assertRaises(exceptions.NotJumpFactInEventGroupError, activate_events, self.kb)
        self.check_in_knowledge_base(self.kb, facts)


class RemoveBrokenStatesTests(TransformatorsTestsBase):

    def setUp(self):
        super(RemoveBrokenStatesTests, self).setUp()


    def test_no_broken_states(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts
        activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_single_broken_state(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts

        broken_state = State(uid='st_broken')

        self.kb += broken_state
        remove_broken_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertFalse(broken_state.uid in self.kb)

    def test_broken_jumps(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts

        broken_jump_from = Jump(state_from='st_broken_state', state_to='st_finish')
        broken_jump_to = Jump(state_from=Start.UID, state_to='st_broken_state')

        self.kb += (broken_jump_from, broken_jump_to)

        remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertFalse(broken_jump_from.uid in self.kb)
        self.assertFalse(broken_jump_to.uid in self.kb)

    def test_broken_path(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts

        broken_path = [State(uid='st_broken_1'),
                       State(uid='st_broken_2'),
                       Jump(state_from='st_broken_1', state_to='st_broken_2'),
                       Jump(state_from='st_broken_w', state_to='st_finish')]

        self.kb += broken_path

        remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, broken_path)

    def test_finish_at_not_finish_state(self):
        facts = [ Start(),
                  Finish(uid='st_finish'),
                  Jump(state_from=Start.UID, state_to='st_finish') ]
        self.kb += facts

        broken_path = [State(uid='st_broken_1'),
                       Jump(state_from=Start.UID, state_to='st_broken_1')]

        self.kb += broken_path

        remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, broken_path)

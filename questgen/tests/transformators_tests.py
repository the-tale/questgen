# coding: utf-8

import unittest

from questgen import exceptions
from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Start, State, Jump, Finish, Event, OnlyGoodBranches, OnlyBadBranches, GivePower, Choice, Option, OptionsLink, ChoicePath
from questgen import transformators


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
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_no_tag(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish'),
                  Event(uid='event_tag') ]
        self.kb += facts
        self.assertRaises(exceptions.NoTaggedEventMembersError, transformators.activate_events, self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_simple_tagged_jump(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish', tags=('event_tag', )),
                  Event(uid='event_tag') ]
        self.kb += facts
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_multiple_tagged_jump(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Event(uid='event_tag') ]
        self.kb += facts

        jump_1 = Jump(state_from='start', state_to='st_finish_1', tags=('event_tag', ))
        jump_2 = Jump(state_from='start', state_to='st_finish_2', tags=('event_tag', ))

        self.kb += (jump_1, jump_2)

        transformators.activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertTrue( (jump_1.uid in self.kb and jump_2.uid not in self.kb) or
                         (jump_2.uid in self.kb and jump_1.uid not in self.kb) )

    def test_multiple_events_jump_marked_for_multiple_events(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Event(uid='event_tag'),
                  Event(uid='event_2_tag')]
        self.kb += facts

        jump_1 = Jump(state_from='start', state_to='st_finish_1', tags=('event_tag', 'event_2_tag'))
        jump_2 = Jump(state_from='start', state_to='st_finish_2', tags=('event_tag',))

        self.kb += (jump_1, jump_2)

        self.assertRaises(exceptions.MoreThenOneEventTagError, transformators.activate_events, self.kb)

    def test_multiple_events(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish_1'),
                  Finish(uid='st_finish_2'),
                  Finish(uid='st_finish_3'),
                  Finish(uid='st_finish_4'),
                  Event(uid='event_tag'),
                  Event(uid='event_2_tag')]

        self.kb += facts

        jump_1 = Jump(state_from='start', state_to='st_finish_1', tags=('event_tag',))
        jump_2 = Jump(state_from='start', state_to='st_finish_2', tags=('event_tag',))
        jump_3 = Jump(state_from='start', state_to='st_finish_3', tags=('event_2_tag',))
        jump_4 = Jump(state_from='start', state_to='st_finish_4', tags=('event_2_tag',))

        self.kb += (jump_1, jump_2, jump_3, jump_4)

        transformators.activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertTrue( (jump_1.uid in self.kb and jump_2.uid not in self.kb) or
                         (jump_2.uid in self.kb and jump_1.uid not in self.kb) )
        self.assertTrue( (jump_3.uid in self.kb and jump_4.uid not in self.kb) or
                         (jump_4.uid in self.kb and jump_3.uid not in self.kb) )



class RemoveBrokenStatesTests(TransformatorsTestsBase):

    def setUp(self):
        super(RemoveBrokenStatesTests, self).setUp()


    def test_no_broken_states(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_single_broken_state(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts

        broken_state = State(uid='st_broken')

        self.kb += broken_state
        transformators.remove_broken_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertFalse(broken_state.uid in self.kb)

    def test_broken_jumps(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts

        broken_jump_from = Jump(state_from='st_broken_state', state_to='st_finish')
        broken_jump_to = Jump(state_from='start', state_to='st_broken_state')

        self.kb += (broken_jump_from, broken_jump_to)

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.assertFalse(broken_jump_from.uid in self.kb)
        self.assertFalse(broken_jump_to.uid in self.kb)

    def test_broken_path(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts

        broken_path = [State(uid='st_broken_1'),
                       State(uid='st_broken_2'),
                       Jump(state_from='st_broken_1', state_to='st_broken_2'),
                       Jump(state_from='st_broken_2', state_to='st_finish')]

        self.kb += broken_path

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, broken_path)

    def test_finish_at_not_finish_state(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts

        broken_path = [State(uid='st_broken_1'),
                       Jump(state_from='start', state_to='st_broken_1')]

        self.kb += broken_path

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, broken_path)


class RemoveRestrictedStatesTests(TransformatorsTestsBase):

    def setUp(self):
        super(RemoveRestrictedStatesTests, self).setUp()

    def test_no_restricted_states(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_has_restricted_states(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish', actions=[GivePower(person='person_1', power=1), GivePower(person='person_2', power=-1)]),
                  Jump(state_from='start', state_to='st_finish'),
                  OnlyGoodBranches(person='person_1'),
                  OnlyBadBranches(person='person_2')]
        self.kb += facts
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_only_good_branches(self):
        facts = [ Start(uid='start', type='test'),
                  Jump(state_from='start', state_to='st_finish'),
                  OnlyGoodBranches(person='person')]
        self.kb += facts
        self.kb += Finish(uid='st_finish', actions=[GivePower(person='person', power=-1)]),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)

    def test_only_bad_branches(self):
        facts = [ Start(uid='start', type='test'),
                  Jump(state_from='start', state_to='st_finish'),
                  OnlyBadBranches(person='person')]
        self.kb += facts
        self.kb += Finish(uid='st_finish', actions=[GivePower(person='person', power=1)]),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts)



class DetermineDefaultChoicesTests(TransformatorsTestsBase):

    def setUp(self):
        super(DetermineDefaultChoicesTests, self).setUp()

    def test_no_choices(self):
        facts = [ Start(uid='start', type='test'),
                  Finish(uid='st_finish'),
                  Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertEqual(len(list(self.kb.filter(OptionsLink))), 0)

    def test_one_choice(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        facts = [ start,
                  choice_1,
                  finish_1,
                  finish_2,
                  Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1'),
                  Option(state_from=choice_1.uid, state_to=finish_2.uid, type='opt_2') ]
        self.kb += facts
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertEqual(len(list(self.kb.filter(OptionsLink))), 0)
        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 1)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(ChoicePath)])), 1)

    def test_two_choices(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        choice_2 = Choice(uid='choice_2')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2]

        self.kb += facts
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertEqual(len(list(self.kb.filter(OptionsLink))), 0)
        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(ChoicePath)])), 2)


    def test_linked_choices(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        choice_2 = Choice(uid='choice_2')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  OptionsLink(options=(option_2.uid, option_2_2.uid))]

        self.kb += facts
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(ChoicePath)])), 2)

        chosen_options = set([path.option for path in self.kb.filter(ChoicePath)])
        self.assertTrue(chosen_options == set([option_1.uid, option_2_1.uid]) or chosen_options == set([option_2.uid, option_2_2.uid]) )

    def test_linked_choices__option_with_two_links(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        choice_2 = Choice(uid='choice_2')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  OptionsLink(options=(option_2.uid, option_2_2.uid, option_1.uid))]

        self.kb += facts
        self.assertRaises(exceptions.OptionWithTwoLinksError, transformators.determine_default_choices, self.kb)
        self.check_in_knowledge_base(self.kb, facts)
        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 0)

    def test_linked_choices__linked_option_with_processed_choice(self):
        # exception raised when first processed choice_1 and choice is option_2
        # since it is random behaviour, we can test ony random exception raising

        is_raised = False

        for i in xrange(100):
            kb = KnowledgeBase()
            start = Start(uid='start', type='test')
            choice_1 = Choice(uid='choice_1')
            choice_2 = Choice(uid='choice_2')
            finish_1 = Finish(uid='finish_1')
            finish_2 = Finish(uid='finish_2')

            option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
            option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

            option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
            option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

            facts = [ start,
                      choice_1,
                      choice_2,
                      finish_1,
                      finish_2,

                      option_1,
                      option_2,
                      option_2_1,
                      option_2_2,

                      OptionsLink(options=(option_2.uid, option_2_2.uid))]

            kb += facts

            try:
                transformators.determine_default_choices(kb)
            except exceptions.LinkedOptionWithProcessedChoiceError:
                is_raised = True
                self.assertEqual(len(list(kb.filter(ChoicePath))), 1)
                self.assertEqual([path.choice for path in kb.filter(ChoicePath)], [choice_2.uid])
                self.assertEqual([path.option for path in kb.filter(ChoicePath)], [option_2_1.uid])
                break

        self.assertTrue(is_raised)



class ChangeChoiceTests(TransformatorsTestsBase):

    def setUp(self):
        super(ChangeChoiceTests, self).setUp()

    def test_single_choice(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        choice_2 = Choice(uid='choice_2')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)
                ]

        self.kb += facts

        choices = [ChoicePath(choice=choice_1.uid, option=option_2.uid, default=True)]

        self.kb += choices

        transformators.change_choice(self.kb, choice_1.uid, option_1.uid, default=False)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, choices)

        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(ChoicePath)])), 2)

        self.assertEqual(set([path.option for path in self.kb.filter(ChoicePath)]),
                         set([option_1.uid, option_2_2.uid]))


    def test_linked_choices(self):
        start = Start(uid='start', type='test')
        choice_1 = Choice(uid='choice_1')
        choice_2 = Choice(uid='choice_2')
        finish_1 = Finish(uid='finish_1')
        finish_2 = Finish(uid='finish_2')

        option_1 = Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  OptionsLink(options=(option_2.uid, option_2_2.uid))
                ]

        self.kb += facts

        choices = [ChoicePath(choice=choice_1.uid, option=option_2.uid, default=True),
                   ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)]

        self.kb += choices

        transformators.change_choice(self.kb, choice_1.uid, option_1.uid, default=False)

        self.check_in_knowledge_base(self.kb, facts)
        self.check_not_in_knowledge_base(self.kb, choices)

        self.assertEqual(len(list(self.kb.filter(ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(ChoicePath)])), 2)

        self.assertEqual(set([path.option for path in self.kb.filter(ChoicePath)]),
                         set([option_1.uid, option_2_1.uid]))

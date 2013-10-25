# coding: utf-8

import unittest

from questgen import exceptions
from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen import transformators
from questgen.quests.base_quest import RESULTS


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
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_no_tag(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish'),
                       facts.Event(uid='event_tag', members=()) ]
        self.kb += facts_list
        self.assertRaises(exceptions.NoEventMembersError, transformators.activate_events, self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_simple_tagged_jump(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish'),
                       facts.Event(uid='event_tag', members=('st_finish', )) ]
        self.kb += facts_list
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_multiple_tagged_jump(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Event(uid='event_tag', members=('st_finish_1', 'st_finish_2')) ]
        finishes = [ facts.Finish(uid='st_finish_1', results={}, nesting=0, start='start'),
                     facts.Finish(uid='st_finish_2', results={}, nesting=0, start='start'),]
        self.kb += facts_list
        self.kb += finishes

        transformators.activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertTrue( ('st_finish_1' in self.kb and 'st_finish_2' not in self.kb) or
                         ('st_finish_2' in self.kb and 'st_finish_1' not in self.kb) )

    def test_multiple_events(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Event(uid='event_tag', members=('st_finish_1', 'st_finish_2')),
                       facts.Event(uid='event_2_tag', members=('st_finish_3', 'st_finish_4'))]

        finishes = [ facts.Finish(uid='st_finish_1', results={}, nesting=0, start='start'),
                     facts.Finish(uid='st_finish_2', results={}, nesting=0, start='start'),
                     facts.Finish(uid='st_finish_3', results={}, nesting=0, start='start'),
                     facts.Finish(uid='st_finish_4', results={}, nesting=0, start='start') ]

        self.kb += facts_list
        self.kb += finishes

        transformators.activate_events(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertTrue( ('st_finish_1' in self.kb and 'st_finish_2' not in self.kb) or
                         ('st_finish_2' in self.kb and 'st_finish_1' not in self.kb) )
        self.assertTrue( ('st_finish_3' in self.kb and 'st_finish_4' not in self.kb) or
                         ('st_finish_4' in self.kb and 'st_finish_3' not in self.kb) )



class RemoveBrokenStatesTests(TransformatorsTestsBase):

    def setUp(self):
        super(RemoveBrokenStatesTests, self).setUp()


    def test_no_broken_states(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list
        transformators.activate_events(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_single_broken_state(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_state = facts.State(uid='st_broken')

        self.kb += broken_state
        transformators.remove_broken_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertFalse(broken_state.uid in self.kb)

    def test_single_broken_start(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_facts = [ facts.Start(uid='start_broken', type='test', nesting=1),
                         facts.Jump(state_from='start_broken', state_to='st_finish') ]

        self.kb += broken_facts

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, broken_facts)

    def test_single_broken_finish(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_facts = [ facts.Finish(uid='finish_broken', results={}, nesting=1, start='start'),
                         facts.Jump(state_from='start', state_to='finish_broken') ]

        self.kb += broken_facts

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, broken_facts)

    def test_broken_jumps(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_jump_from = facts.Jump(state_from='st_broken_state', state_to='st_finish')
        broken_jump_to = facts.Jump(state_from='start', state_to='st_broken_state')

        self.kb += (broken_jump_from, broken_jump_to)

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertFalse(broken_jump_from.uid in self.kb)
        self.assertFalse(broken_jump_to.uid in self.kb)

    def test_broken_linked_options(self):
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')

        o_1_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='o')
        o_1_f1 = facts.Option(state_from=choice_1.uid, state_to='st_finish_1', type='o')
        o_2_f1 = facts.Option(state_from=choice_2.uid, state_to='st_finish_1', type='o')
        o_2_f2 = facts.Option(state_from=choice_2.uid, state_to='st_finish_2', type='o')

        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Jump(state_from='start', state_to=choice_1.uid),
                       choice_1,
                       o_1_f1,
                       facts.Finish(uid='st_finish_1', results={}, nesting=0, start='start')]

        self.kb += facts_list

        broken = [choice_2,
                  o_1_2,
                  o_2_f1,
                  o_2_f2,
                  facts.Finish(uid='st_finish_2', results={}, nesting=1, start='start')]

        self.kb += broken

        self.kb += [facts.OptionsLink(options=[o_1_2.uid, o_2_f2.uid])]

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, broken)

    def test_broken_path(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_path = [facts.State(uid='st_broken_1'),
                       facts.State(uid='st_broken_2'),
                       facts.Jump(state_from='st_broken_1', state_to='st_broken_2'),
                       facts.Jump(state_from='st_broken_2', state_to='st_finish')]

        self.kb += broken_path

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, broken_path)

    def test_finish_at_not_finish_state(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                       facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                       facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list

        broken_path = [facts.State(uid='st_broken_1'),
                       facts.Jump(state_from='start', state_to='st_broken_1')]

        self.kb += broken_path

        transformators.remove_broken_states(self.kb)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, broken_path)


class RemoveRestrictedStatesTests(TransformatorsTestsBase):

    def setUp(self):
        super(RemoveRestrictedStatesTests, self).setUp()

    def test_no_restricted_states(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                  facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_has_restricted_states(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Person(uid='person_1'),
                  facts.Person(uid='person_2'),
                  facts.Finish(uid='st_finish',
                               results={'person_1': RESULTS.SUCCESSED,
                                        'person_2': RESULTS.FAILED},
                               nesting=0,
                               start='start'),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.OnlyGoodBranches(object='person_1'),
                  facts.OnlyBadBranches(object='person_2')]
        self.kb += facts_list
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_only_good_branches__person(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.OnlyGoodBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.FAILED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_only_bad_branches__person(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.OnlyBadBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.SUCCESSED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)


    def test_only_good_branches__place(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Place(uid='place'),
                  facts.OnlyGoodBranches(object='place')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'place': RESULTS.FAILED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_only_bad_branches__place(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Place(uid='place'),
                  facts.OnlyBadBranches(object='place')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'place': RESULTS.SUCCESSED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)


    def test_except_good_branches__successed(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.ExceptGoodBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.SUCCESSED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)


    def test_except_good_branches__neutral(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.ExceptGoodBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.NEUTRAL},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_except_bad_branches__failed(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.OnlyBadBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.FAILED},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)

    def test_except_bad_branches__neutral(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Jump(state_from='start', state_to='st_finish'),
                  facts.Person(uid='person'),
                  facts.OnlyBadBranches(object='person')]
        self.kb += facts_list
        self.kb += facts.Finish(uid='st_finish',
                                results={'person': RESULTS.NEUTRAL},
                                nesting=0,
                                start='start'),
        transformators.remove_restricted_states(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)





class DetermineDefaultChoicesTests(TransformatorsTestsBase):

    def setUp(self):
        super(DetermineDefaultChoicesTests, self).setUp()

    def test_no_choices(self):
        facts_list = [ facts.Start(uid='start', type='test', nesting=0),
                  facts.Finish(uid='st_finish', results={}, nesting=0, start='start'),
                  facts.Jump(state_from='start', state_to='st_finish') ]
        self.kb += facts_list
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertEqual(len(list(self.kb.filter(facts.OptionsLink))), 0)

    def test_one_choice(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        facts_list = [ start,
                  choice_1,
                  finish_1,
                  finish_2,
                  facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1'),
                  facts.Option(state_from=choice_1.uid, state_to=finish_2.uid, type='opt_2') ]
        self.kb += facts_list
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertEqual(len(list(self.kb.filter(facts.OptionsLink))), 0)
        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 1)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(facts.ChoicePath)])), 1)

    def test_two_choices(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts_list = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2]

        self.kb += facts_list
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertEqual(len(list(self.kb.filter(facts.OptionsLink))), 0)
        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(facts.ChoicePath)])), 2)


    def test_linked_choices(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts_list = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  facts.OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  facts.OptionsLink(options=(option_2.uid, option_2_2.uid))]

        self.kb += facts_list
        transformators.determine_default_choices(self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(facts.ChoicePath)])), 2)

        chosen_options = set([path.option for path in self.kb.filter(facts.ChoicePath)])
        self.assertTrue(chosen_options == set([option_1.uid, option_2_1.uid]) or chosen_options == set([option_2.uid, option_2_2.uid]) )

    def test_linked_choices__option_with_two_links(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts_list = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  facts.OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  facts.OptionsLink(options=(option_2.uid, option_2_2.uid, option_1.uid))]

        self.kb += facts_list
        self.assertRaises(exceptions.OptionWithTwoLinksError, transformators.determine_default_choices, self.kb)
        self.check_in_knowledge_base(self.kb, facts_list)
        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 0)

    def test_linked_choices__linked_option_with_processed_choice(self):
        is_raised = False

        for i in xrange(100):
            kb = KnowledgeBase()
            start = facts.Start(uid='start', type='test', nesting=0)
            choice_1 = facts.Choice(uid='choice_1')
            choice_2 = facts.Choice(uid='choice_2')
            finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
            finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

            option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
            option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

            option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
            option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

            facts_list = [ start,
                           facts.Jump(state_from=start.uid, state_to=choice_1.uid),
                           choice_1,
                           choice_2,
                           finish_1,
                           finish_2,

                           option_1,
                           option_2,
                           option_2_1,
                           option_2_2,

                           facts.OptionsLink(options=(option_2.uid, option_2_2.uid))]

            kb += facts_list

            try:
                transformators.determine_default_choices(kb)
            except exceptions.LinkedOptionWithProcessedChoiceError:
                is_raised = True
                self.assertEqual(len(list(kb.filter(facts.ChoicePath))), 1)
                self.assertEqual([path.choice for path in kb.filter(facts.ChoicePath)], [choice_2.uid])
                self.assertEqual([path.option for path in kb.filter(facts.ChoicePath)], [option_2_1.uid])
                break

        self.assertFalse(is_raised)

class ChangeChoiceTests(TransformatorsTestsBase):

    def setUp(self):
        super(ChangeChoiceTests, self).setUp()

    def test_single_choice(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts_list = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  facts.ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)
                ]

        self.kb += facts_list

        choices = [facts.ChoicePath(choice=choice_1.uid, option=option_2.uid, default=True)]

        self.kb += choices

        transformators.change_choice(self.kb, option_1.uid, default=False)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, choices)

        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(facts.ChoicePath)])), 2)

        self.assertEqual(set([path.option for path in self.kb.filter(facts.ChoicePath)]),
                         set([option_1.uid, option_2_2.uid]))


    def test_linked_choices(self):
        start = facts.Start(uid='start', type='test', nesting=0)
        choice_1 = facts.Choice(uid='choice_1')
        choice_2 = facts.Choice(uid='choice_2')
        finish_1 = facts.Finish(uid='finish_1', results={}, nesting=0, start='start')
        finish_2 = facts.Finish(uid='finish_2', results={}, nesting=0, start='start')

        option_1 = facts.Option(state_from=choice_1.uid, state_to=finish_1.uid, type='opt_1')
        option_2 = facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2')

        option_2_1 = facts.Option(state_from=choice_2.uid, state_to=finish_1.uid, type='opt_2_1')
        option_2_2 = facts.Option(state_from=choice_2.uid, state_to=finish_2.uid, type='opt_2_2')

        facts_list = [ start,
                  choice_1,
                  choice_2,
                  finish_1,
                  finish_2,

                  option_1,
                  option_2,
                  option_2_1,
                  option_2_2,

                  facts.OptionsLink(options=(option_1.uid, option_2_1.uid)),
                  facts.OptionsLink(options=(option_2.uid, option_2_2.uid))
                ]

        self.kb += facts_list

        choices = [facts.ChoicePath(choice=choice_1.uid, option=option_2.uid, default=True),
                   facts.ChoicePath(choice=choice_2.uid, option=option_2_2.uid, default=True)]

        self.kb += choices

        transformators.change_choice(self.kb, option_1.uid, default=False)

        self.check_in_knowledge_base(self.kb, facts_list)
        self.check_not_in_knowledge_base(self.kb, choices)

        self.assertEqual(len(list(self.kb.filter(facts.ChoicePath))), 2)
        self.assertEqual(len(set([path.choice for path in self.kb.filter(facts.ChoicePath)])), 2)

        self.assertEqual(set([path.option for path in self.kb.filter(facts.ChoicePath)]),
                         set([option_1.uid, option_2_1.uid]))

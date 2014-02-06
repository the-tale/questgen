# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen import restrictions

class RestrictionsTestsBase(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()


class CommonRestrictionsTests(RestrictionsTestsBase):

    def test_always_success(self):
        restrictions.AlwaysSuccess().validate(self.kb)

    def test_always_error(self):
        self.assertRaises(restrictions.AlwaysError.Error, restrictions.AlwaysError().validate, self.kb)


class SingleStartStateWithNoEntersTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleStartStateWithNoEntersTests, self).setUp()
        self.start = facts.Start(uid='start', type='test', nesting=0)
        self.restriction = restrictions.SingleStartStateWithNoEnters()

    def test_success(self):
        self.kb += self.start
        self.restriction.validate(self.kb)

    def test_no_start(self):
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_start__without_enters(self):
        self.kb += ( self.start,
                     facts.Start(uid='start_2', type='test', nesting=0) )
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_start__with_enters(self):
        self.kb += ( self.start,
                     facts.Start(uid='start_2', type='test', nesting=0),
                     facts.Jump(state_from=self.start.uid, state_to='start_2'))
        self.restriction.validate(self.kb)


class FinishStateExistsTests(RestrictionsTestsBase):

    def setUp(self):
        super(FinishStateExistsTests, self).setUp()
        self.finish = facts.Finish(start='start', uid='finish', results={}, nesting=0)
        self.restriction = restrictions.FinishStateExists()

    def test_success(self):
        self.kb += self.finish
        self.restriction.validate(self.kb)

    def test_no_finish(self):
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_finish(self):
        self.kb += self.finish
        self.kb += facts.Finish(start='start', uid='finish_2', results={}, nesting=0)
        self.restriction.validate(self.kb)


class AllStatesHasJumpsTests(RestrictionsTestsBase):

    def setUp(self):
        super(AllStatesHasJumpsTests, self).setUp()
        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.State(uid='state_1'),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    facts.Jump(state_from='state_1', state_to='finish_1')]
        self.restriction = restrictions.AllStatesHasJumps()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_error(self):
        self.kb += [facts.State(uid='state_2'),
                    facts.Jump(state_from='start', state_to='state_2')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class SingleLocationForObjectTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleLocationForObjectTests, self).setUp()
        self.restriction = restrictions.SingleLocationForObject()

    def test_success(self):
        self.kb += facts.LocatedIn(object='person', place='place')
        self.restriction.validate(self.kb)

    def test_no_location(self):
        self.restriction.validate(self.kb)

    def test_more_then_one_location__for_person(self):
        self.kb += [ facts.LocatedIn(object='person', place='place'),
                     facts.LocatedIn(object='person', place='place_2')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_location__for_person__diferent_relations(self):
        self.kb += [ facts.LocatedIn(object='person', place='place'),
                     facts.LocatedNear(object='person', place='place_2')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_location__for_place(self):
        self.kb += [ facts.LocatedIn(object='person', place='place'),
                     facts.LocatedIn(object='person_2', place='place')]
        self.restriction.validate(self.kb)

    def test_more_then_one_location__for_place__diferent_relations(self):
        self.kb += [ facts.LocatedNear(object='person', place='place'),
                     facts.LocatedIn(object='person_2', place='place')]
        self.restriction.validate(self.kb)


class ReferencesIntegrityTests(RestrictionsTestsBase):

    def setUp(self):
        super(ReferencesIntegrityTests, self).setUp()
        self.restriction = restrictions.ReferencesIntegrity()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_none_value(self):
        self.kb += [facts.Person(uid='person'),
                    facts.LocatedIn(object='person', place=None) ]
        self.restriction.validate(self.kb)

    def test_bad_reference(self):
        self.kb += facts.LocatedIn(object='person', place=None)
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class RequirementsConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(RequirementsConsistencyTests, self).setUp()
        self.restriction = restrictions.RequirementsConsistency()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_wrong_require(self):
        self.kb += [facts.State(uid='state', require=[facts.Place(uid='wrong requirement')])]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_wrong_condition(self):
        self.kb += [facts.Question(uid='state', condition=[facts.Place(uid='wrong requirement')])]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class ActionsConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(ActionsConsistencyTests, self).setUp()
        self.restriction = restrictions.ActionsConsistency()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_wrong_action(self):
        self.kb += [facts.State(uid='state', actions=[facts.Place(uid='wrong action')])]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_wrong_start_action(self):
        self.kb += [facts.Jump(state_from='start', state_to='state_1', start_actions=[facts.Place(uid='wrong action')])]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_wrong_end_action(self):
        self.kb += [facts.Jump(state_from='start', state_to='state_1', end_actions=[facts.Place(uid='wrong action')])]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)



class ConnectedStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(ConnectedStateJumpGraphTests, self).setUp()
        self.restriction = restrictions.ConnectedStateJumpGraph()

        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.State(uid='state_1'),
                    facts.Start(uid='start_2', type='test', nesting=1),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Finish(start='start', uid='finish_2', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    facts.Jump(state_from='state_1', state_to='start_2'),
                    facts.Jump(state_from='state_1', state_to='finish_1'),
                    facts.Jump(state_from='start_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += [facts.State(uid='state_3'),
                    facts.State(uid='state_4'),
                    facts.Jump(state_from='state_3', state_to='state_4')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class NoCirclesInStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(NoCirclesInStateJumpGraphTests, self).setUp()
        self.restriction = restrictions.NoCirclesInStateJumpGraph()

        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.State(uid='state_1'),
                    facts.State(uid='state_2'),
                    facts.Start(uid='start_3', type='test', nesting=0),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    facts.Jump(state_from='state_1', state_to='state_2'),
                    facts.Jump(state_from='state_2', state_to='start_3'),
                    facts.Jump(state_from='start_3', state_to='finish_1')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += facts.Jump(state_from='start_3', state_to='state_1')
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class MultipleJumpsFromNormalStateTests(RestrictionsTestsBase):

    def setUp(self):
        super(MultipleJumpsFromNormalStateTests, self).setUp()
        self.restriction = restrictions.MultipleJumpsFromNormalState()

        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.Choice(uid='state_1'),
                    facts.State(uid='state_2'),
                    facts.Question(uid='state_3', condition=()),
                    facts.Jump(state_from='state_2', state_to='state_3'),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Finish(start='start', uid='finish_2', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    facts.Option(state_from='state_1', state_to='state_2', type='opt_1', markers=()),
                    facts.Option(state_from='state_1', state_to='finish_1', type='opt_2', markers=()),
                    facts.Answer(state_from='state_3', state_to='finish_1', condition=True),
                    facts.Answer(state_from='state_3', state_to='finish_2', condition=False)  ]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += facts.Jump(state_from='state_2', state_to='finish_1')
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class ChoicesConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(ChoicesConsistencyTests, self).setUp()
        self.restriction = restrictions.ChoicesConsistency()

        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.Choice(uid='state_1'),
                    facts.State(uid='state_2'),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Finish(start='start', uid='finish_2', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    facts.Option(state_from='state_1', state_to='state_2', type='opt_1', markers=()),
                    facts.Option(state_from='state_1', state_to='finish_1', type='opt_2', markers=()),
                    facts.Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_option_like_jump(self):
        self.kb += facts.Option(state_from='state_2', state_to='finish_1', type='opt_3', markers=())
        self.assertRaises(self.restriction.OptionLikeJumpError, self.restriction.validate, self.kb)

    def test_jump_like_option(self):
        self.kb += facts.Jump(state_from='state_1', state_to='finish_1')
        self.assertRaises(self.restriction.JumpLikeOptionError, self.restriction.validate, self.kb)


class QuestionsConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(QuestionsConsistencyTests, self).setUp()
        self.restriction = restrictions.QuestionsConsistency()

        self.answer_1 = facts.Answer(state_from='state_1', state_to='state_2', condition=True)
        self.answer_2 = facts.Answer(state_from='state_1', state_to='finish_1', condition=False)

        self.kb += [facts.Start(uid='start', type='test', nesting=0),
                    facts.Question(uid='state_1', condition=()),
                    facts.State(uid='state_2'),
                    facts.Finish(start='start', uid='finish_1', results={}, nesting=0),
                    facts.Finish(start='start', uid='finish_2', results={}, nesting=0),
                    facts.Jump(state_from='start', state_to='state_1'),
                    self.answer_1,
                    self.answer_2,
                    facts.Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_answer_like_jump(self):
        self.kb += facts.Answer(state_from='state_2', state_to='finish_1', condition=True)
        self.assertRaises(self.restriction.AnswerLikeJumpError, self.restriction.validate, self.kb)

    def test_jump_like_option(self):
        self.kb += facts.Jump(state_from='state_1', state_to='finish_1')
        self.assertRaises(self.restriction.JumpLikeAnswerError, self.restriction.validate, self.kb)

    def test_wrong_answers_number__more_then_2_answers(self):
        self.kb += facts.Answer(state_from='state_1', state_to='finish_1', condition=True)
        self.assertRaises(self.restriction.WrongAnswersNumber, self.restriction.validate, self.kb)

    def test_wrong_answers_number__less_then_2_answers(self):
        self.kb -= self.answer_1
        self.assertRaises(self.restriction.WrongAnswersNumber, self.restriction.validate, self.kb)

    def test_wrong_answers_structure__true(self):
        self.kb -= self.answer_2
        self.kb += facts.Answer(state_from='state_1', state_to='finish_1', condition=True)
        self.assertRaises(self.restriction.WrongAnswersStructure, self.restriction.validate, self.kb)

    def test_wrong_answers_structure__false(self):
        self.kb -= self.answer_1
        self.kb += facts.Answer(state_from='state_1', state_to='state_2', condition=False)
        self.assertRaises(self.restriction.WrongAnswersStructure, self.restriction.validate, self.kb)


class FinishResultsConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(FinishResultsConsistencyTests, self).setUp()
        self.restriction = restrictions.FinishResultsConsistency()

        self.finish_1 = facts.Finish(start='start_1', uid='finish_1', results={'p1': 0, 'p2': 0}, nesting=0)
        self.finish_2 = facts.Finish(start='start_2', uid='finish_2', results={'p3': 0, 'p4': 0, 'p5': 0}, nesting=0)

        self.kb += [facts.Start(uid='start_1', type='test', nesting=0),
                    facts.Start(uid='start_2', type='test', nesting=0),
                    self.finish_1,
                    self.finish_2,
                    facts.QuestParticipant(start='start_1', participant='p1', role='role'),
                    facts.QuestParticipant(start='start_1', participant='p2', role='role'),
                    facts.QuestParticipant(start='start_2', participant='p3', role='role'),
                    facts.QuestParticipant(start='start_2', participant='p4', role='role'),
                    facts.QuestParticipant(start='start_2', participant='p5', role='role')]


    def test_success(self):
        self.restriction.validate(self.kb)

    def test_participant_not_in_results__1(self):
        del self.finish_1.results['p2']
        self.assertRaises(self.restriction.ParticipantNotInResults, self.restriction.validate, self.kb)

    def test_participant_not_in_results__2(self):
        del self.finish_2.results['p4']
        self.assertRaises(self.restriction.ParticipantNotInResults, self.restriction.validate, self.kb)

    def test_wrong_participant_in_results__1(self):
        self.finish_1.results['p3'] = 0
        self.assertRaises(self.restriction.ParticipantNotExists, self.restriction.validate, self.kb)

    def test_wrong_participant_in_results__2(self):
        self.finish_2.results['p1'] = 0
        self.assertRaises(self.restriction.ParticipantNotExists, self.restriction.validate, self.kb)

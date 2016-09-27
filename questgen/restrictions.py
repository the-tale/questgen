# coding: utf-8
import itertools

from questgen import facts
from questgen import exceptions
from questgen import logic
from questgen import requirements
from questgen import actions


class Restriction(object):

    def validate(self, knowledge_base):
        raise NotImplementedError


class AlwaysSuccess(Restriction):
    def validate(self, knowledge_base): pass


class AlwaysError(Restriction):

    class Error(exceptions.RollBackError):
        MSG = 'Always error'

    def validate(self, knowledge_base):
        raise self.Error()


class SingleStartStateWithNoEnters(Restriction):

    class Error(exceptions.RollBackError):
        MSG = 'MUST be only one Start statement without entering jumps'

    def validate(self, knowledge_base):
        enter_uids = set(jump.state_to for jump in knowledge_base.filter(facts.Jump))
        starts = (start for start in knowledge_base.filter(facts.Start) if start.uid not in enter_uids)

        if len(list(starts)) != 1:
            raise self.Error()


class FinishStateExists(Restriction):

    class Error(exceptions.RollBackError):
        MSG = 'at least one Finish state MUST exists'

    def validate(self, knowledge_base):
        if len(list(knowledge_base.filter(facts.Finish))) == 0:
            raise self.Error()


class AllStatesHasJumps(Restriction):

    class Error(exceptions.RollBackError):
        MSG = 'no jumps from state "%(state)s"'

    def validate(self, knowledge_base):
        from_uids = set(jump.state_from for jump in knowledge_base.filter(facts.Jump))
        for state in knowledge_base.filter(facts.State):
            if not isinstance(state, facts.Finish) and state.uid not in from_uids:
                raise self.Error(state=state)


class SingleLocationForObject(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'every person MUST be located in single place. Problem in %(location_1)r and %(location_2)s'

    def validate(self, knowledge_base):
        objects_to_locations = {}
        for location in itertools.chain(knowledge_base.filter(facts.LocatedIn), knowledge_base.filter(facts.LocatedNear)):
            if location.object in objects_to_locations:
                raise self.Error(location_1=location,
                                 location_2=objects_to_locations[location.object])
            objects_to_locations[location.object] = location


class ReferencesIntegrity(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'bad reference in fact "%(fact)s" in "%(attribute)s": "%(uid)s"'

    def validate(self, knowledge_base):
        for fact in knowledge_base.facts():
            for reference in fact._references:

                uid = getattr(fact, reference)
                if uid is not None and uid not in knowledge_base:
                    raise self.Error(fact=fact, attribute=reference, uid=uid)


class RequirementsConsistency(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'wrong class of requirement "%(requirement)s" in state "%(state)s"'

    def validate(self, knowledge_base):
        for state in knowledge_base.filter(facts.State):
            for requirement in state.require:
                if not isinstance(requirement, requirements.Requirement):
                    raise self.Error(requirement=requirement, state=state)

            if isinstance(state, facts.Question):
                for requirement in state.condition:
                    if not isinstance(requirement, requirements.Requirement):
                        raise self.Error(requirement=requirement, state=state)


class ActionsConsistency(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'wrong class of action "%(action)s" in fact "%(fact)s"'

    def validate(self, knowledge_base):
        for state in knowledge_base.filter(facts.State):
            for action in state.actions:
                if not isinstance(action, actions.Action):
                    raise self.Error(action=action, fact=state)

        for jump in knowledge_base.filter(facts.Jump):
            for action in itertools.chain(jump.start_actions, jump.end_actions):
                if not isinstance(action, actions.Action):
                    raise self.Error(action=action, fact=jump)



class ConnectedStateJumpGraph(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'States not reached from absolute Start: %(states)r'

    def validate(self, knowledge_base):
        start_uid = logic.get_absolute_start(knowledge_base).uid

        riched_states = set()
        query = [start_uid]

        while query:
            state_uid = query.pop(0)

            if state_uid in riched_states: continue

            riched_states.add(state_uid)

            for jump in knowledge_base.filter(facts.Jump):
                if jump.state_from != state_uid: continue
                query.append(jump.state_to)

        all_states = set(state.uid for state in knowledge_base.filter(facts.State))

        if riched_states != all_states:
            raise self.Error(states=all_states-riched_states)


class NoCirclesInStateJumpGraph(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'Jumps in circle: %(jumps)r'

    def _bruteforce(self, path, table):
        current_state = path[-1]

        if not table.get(current_state):
            return

        for next_state in table[current_state]:

            if next_state in path:
                raise self.Error(jumps=path+[next_state])

            path.append(next_state)
            self._bruteforce(path, table)
            path.pop()


    def validate(self, knowledge_base):
        start_uid = logic.get_absolute_start(knowledge_base).uid

        table = {}
        for jump in knowledge_base.filter(facts.Jump):
            if jump.state_from not in table:
                table[jump.state_from] = []
            table[jump.state_from].append(jump.state_to)
        self._bruteforce([start_uid], table)


class MultipleJumpsFromNormalState(Restriction):
    class Error(exceptions.RollBackError):
        MSG = 'States with multiple jumps: %(states)r'

    def validate(self, knowledge_base):

        wrong_states = []

        for state in knowledge_base.filter(facts.State):
            if isinstance(state, (facts.Choice, facts.Question)):
               continue

            jumps = list(jump for jump in knowledge_base.filter(facts.Jump) if jump.state_from == state.uid)

            if len(jumps) > 1:
                wrong_states.append(state.uid)

        if wrong_states:
            raise self.Error(states=wrong_states)


class ChoicesConsistency(Restriction):
    class OptionLikeJumpError(exceptions.RollBackError):
        MSG = 'Option not connected to choice state: %(option)r'

    class JumpLikeOptionError(exceptions.RollBackError):
        MSG = 'Jump connected to choice state: %(jump)r'

    def validate(self, knowledge_base):

        for option in knowledge_base.filter(facts.Option):
            if isinstance(knowledge_base[option.state_from], facts.Choice):
               continue

            raise self.OptionLikeJumpError(option=option)

        for jump in knowledge_base.filter(facts.Jump):
            if not isinstance(knowledge_base[jump.state_from], facts.Choice):
               continue

            if isinstance(jump, facts.Option):
               continue

            raise self.JumpLikeOptionError(jump=jump)



class QuestionsConsistency(Restriction):
    class AnswerLikeJumpError(exceptions.RollBackError):
        MSG = 'Answer not connected to question state: %(answer)r'

    class JumpLikeAnswerError(exceptions.RollBackError):
        MSG = 'Jump connected to Question state: %(jump)r'

    class WrongAnswersNumber(exceptions.RollBackError):
        MSG = '%(question)r must has 2 answers: false & true'

    class WrongAnswersStructure(exceptions.RollBackError):
        MSG = '%(question)r must has 2 answers: false & true'

    def validate(self, knowledge_base):

        for answer in knowledge_base.filter(facts.Answer):
            if isinstance(knowledge_base[answer.state_from], facts.Question):
               continue

            raise self.AnswerLikeJumpError(answer=answer)

        for jump in knowledge_base.filter(facts.Jump):
            if not isinstance(knowledge_base[jump.state_from], facts.Question):
               continue

            if isinstance(jump, facts.Answer):
               continue

            raise self.JumpLikeAnswerError(jump=jump)

        for question in knowledge_base.filter(facts.Question):

            answers = [answer for answer in knowledge_base.filter(facts.Answer) if answer.state_from == question.uid]

            if len(answers) != 2:
                raise self.WrongAnswersNumber(question=question)

            if ( (answers[0].condition and not answers[1].condition) or
                 (not answers[0].condition and answers[1].condition) ):
                continue

            raise self.WrongAnswersStructure(question=question)


class FinishResultsConsistency(Restriction):
    class ParticipantNotInResults(exceptions.RollBackError):
        MSG = 'no result for participant "%(participant)r"'

    class ParticipantNotExists(exceptions.RollBackError):
        MSG = 'no participant for object "%(object)r"'

    def validate(self, knowledge_base):

        for finish in knowledge_base.filter(facts.Finish):
            start = knowledge_base[finish.start]

            participants = set()

            for participant in knowledge_base.filter(facts.QuestParticipant):
                if participant.start != start.uid:
                    continue

                if participant.participant not in finish.results:
                    raise self.ParticipantNotInResults(participant=participant)

                participants.add(participant.participant)

            for object_uid in finish.results:
                if object_uid not in participants:
                    raise self.ParticipantNotExists(object=object_uid)

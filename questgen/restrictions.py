# coding: utf-8
import itertools

from questgen import facts
from questgen import exceptions

class Restriction(object):

    def validate(self, knowledge_base):
        raise NotImplementedError


class AlwaysSuccess(Restriction):
    def validate(self, knowledge_base): pass

class AlwaysError(Restriction):

    class Error(exceptions.RollBackError):
        MSG = u'Always error'

    def validate(self, knowledge_base):
        raise self.Error()


class SingleStartState(Restriction):

    class Error(exceptions.RollBackError):
        MSG = u'MUST be only one Start statement'

    def validate(self, knowledge_base):
        if len(list(knowledge_base.filter(facts.Start))) != 1:
            raise self.Error()

class FinishStateExists(Restriction):

    class Error(exceptions.RollBackError):
        MSG = u'al least one Finish state MUST exists'

    def validate(self, knowledge_base):
        if len(list(knowledge_base.filter(facts.Finish))) == 0:
            raise self.Error()

class NoJumpsFromFinish(Restriction):

    class Error(exceptions.RollBackError):
        MSG = u'MUST be no jumps from finish "%(state)s" states'

    def validate(self, knowledge_base):
        for jump in knowledge_base.filter(facts.Jump):
            if isinstance(knowledge_base[jump.state_from], facts.Finish):
                raise self.Error(state=knowledge_base[jump.state_from])


class SingleLocationForObject(Restriction):
    class Error(exceptions.RollBackError):
        MSG = u'every person MUST be located in single place. Problem in %(location_1)r and %(location_2)s'

    def validate(self, knowledge_base):
        objects_to_locations = {}
        for location in itertools.chain(knowledge_base.filter(facts.LocatedIn), knowledge_base.filter(facts.LocatedNear)):
            if location.object in objects_to_locations:
                raise self.Error(location_1=location,
                                 location_2=objects_to_locations[location.object])
            objects_to_locations[location.object] = location


class ReferencesIntegrity(Restriction):
    class Error(exceptions.RollBackError):
        MSG = u'bad reference in fact "%(fact)s" in "%(attribute)s": "%(uid)s"'

    def validate(self, knowledge_base):
        for fact in knowledge_base.facts():
            for reference in fact._references:

                uid = getattr(fact, reference)
                if uid is not None and uid not in knowledge_base:
                    raise self.Error(fact=fact,
                                     attribute=reference,
                                     uid=uid)

class ConnectedStateJumpGraph(Restriction):
    class Error(exceptions.RollBackError):
        MSG = u'States not reached from Start: %(states)r'

    def validate(self, knowledge_base):
        start_uid = knowledge_base.filter(facts.Start).next().uid

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
        MSG = u'Jumps in circle: %(jumps)r'

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
        start_uid = knowledge_base.filter(facts.Start).next().uid

        table = {}
        for jump in knowledge_base.filter(facts.Jump):
            if jump.state_from not in table:
                table[jump.state_from] = []
            table[jump.state_from].append(jump.state_to)
        self._bruteforce([start_uid], table)


class MultipleJumpsFromNormalState(Restriction):
    class Error(exceptions.RollBackError):
        MSG = u'States with multiple jumps: %(states)r'

    def validate(self, knowledge_base):

        wrong_states = []

        for state in knowledge_base.filter(facts.State):
            if isinstance(state, facts.Choice):
               continue

            jumps = list(jump for jump in knowledge_base.filter(facts.Jump) if jump.state_from == state.uid)

            if len(jumps) > 1:
                wrong_states.append(state.uid)

        if wrong_states:
            raise self.Error(states=wrong_states)


class ChoicesConsistency(Restriction):
    class OptionLikeJumpError(exceptions.RollBackError):
        MSG = u'Option not connected to choice state: %(option)r'

    class JumpLikeOptionError(exceptions.RollBackError):
        MSG = u'Jump connected to choice state: %(jump)r'

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

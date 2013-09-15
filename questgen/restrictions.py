# coding: utf-8

from questgen.facts import Start, LocatedIn, Jump, State, Finish

from questgen.exceptions import QuestgenError

class Restriction(object):

    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base


class AlwaysSuccess(Restriction):
    def validate(self): pass

class AlwaysError(Restriction):

    class Error(QuestgenError):
        MSG = u'Always error'

    def validate(self):
        raise self.Error()


class SingleStartState(Restriction):

    class Error(QuestgenError):
        MSG = u'MUST be only one Start statement'

    def validate(self):
        if len(list(self.knowledge_base.filter(Start))) != 1:
            raise self.Error()

class NoJumpsFromFinish(Restriction):

    class Error(QuestgenError):
        MSG = u'MUST be no jumps from finish "%(state)s" states'

    def validate(self):
        for jump in self.knowledge_base.filter(Jump):
            if isinstance(self.knowledge_base[jump.state_from], Finish):
                raise self.Error(state=self.knowledge_base[jump.state_from])


class SingleLocationForObject(Restriction):
    class Error(QuestgenError):
        MSG = u'every person MUST be located in single place. Problem in %(location_1)r and %(location_2)s'

    def validate(self):
        objects_to_locations = {}
        for location in self.knowledge_base.filter(LocatedIn):
            if location.object in objects_to_locations:
                raise self.Error(location_1=location,
                                 location_2=objects_to_locations[location.object])
            objects_to_locations[location.object] = location


class ReferencesIntegrity(Restriction):
    class Error(QuestgenError):
        MSG = u'bad reference in fact "%(fact)s" in "%(attribute)s": "%(uid)s"'

    def validate(self):
        for fact in self.knowledge_base.facts():
            for reference in fact._references:

                uid = getattr(fact, reference)
                if uid is not None and uid not in self.knowledge_base:
                    raise self.Error(fact=fact,
                                     attribute=reference,
                                     uid=uid)

class ConnectedStateJumpGraph(Restriction):
    class Error(QuestgenError):
        MSG = u'States not reached from Start: %(states)r'

    def validate(self):
        start_uid = self.knowledge_base.filter(Start).next().uid

        riched_states = set()
        query = [start_uid]

        while query:
            state_uid = query.pop(0)

            if state_uid in riched_states: continue

            riched_states.add(state_uid)

            for jump in self.knowledge_base.filter(Jump):
                if jump.state_from != state_uid: continue
                query.append(jump.state_to)

        all_states = set(state.uid for state in self.knowledge_base.filter(State))

        if riched_states != all_states:
            raise self.Error(states=all_states-riched_states)


class NoCirclesInStateJumpGraph(Restriction):
    class Error(QuestgenError):
        MSG = u'Jumps in circle: %(jumps)r'

    def _bruteforce(self, path, table):
        current_state = path[-1]

        if not table.get(current_state):
            return

        if table[current_state][0] in path:
            raise self.Error(jumps=path+[table[current_state][0]])

        for next_state in table[current_state]:
            path.append(table[current_state][0])
            self._bruteforce(path, table)
            path.pop()


    def validate(self):
        start_uid = self.knowledge_base.filter(Start).next().uid

        table = {}
        for jump in self.knowledge_base.filter(Jump):
            if jump.state_from not in table:
                table[jump.state_from] = []
            table[jump.state_from].append(jump.state_to)
        self._bruteforce([start_uid], table)

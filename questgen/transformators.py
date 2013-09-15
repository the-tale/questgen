# coding: utf-8

import random

from questgen.facts import Event, Jump, State, Start, Finish
from questgen import exceptions


def activate_events(knowledge_base):

    choosen_jumps = []
    removed_jumps = []

    events = list(knowledge_base.filter(Event))

    # validate events
    events_tags = set(event.tag for event in events)
    for fact in knowledge_base.facts():
        if  len(events_tags & set(fact.tags)) > 1:
            raise exceptions.MoreThenOneEventTagError(fact=fact)

    # chose events
    for event in events:
        event_jumps = []

        for fact in filter(lambda fact: event.tag in fact.tags, knowledge_base.facts()):

            if not isinstance(fact, Jump):
                raise exceptions.NotJumpFactInEventGroupError(event=event, fact=fact)

            event_jumps.append(fact)

        if not event_jumps:
            raise exceptions.NoTaggedEventMembersError(event=event)

        choosen_jumps.append(random.choice(event_jumps))
        removed_jumps.extend(event_jumps)

    knowledge_base -= set(removed_jumps) - set(choosen_jumps)


def remove_broken_states(knowledge_base):

    while True:
        states_to_remove = []

        for state in knowledge_base.filter(State):
            if isinstance(state, Start):
                pass
            elif not filter(lambda jump: jump.state_to == state.uid, knowledge_base.filter(Jump)):
                states_to_remove.append(state)
            elif isinstance(state, Finish):
                pass
            elif not filter(lambda jump: jump.state_from == state.uid, knowledge_base.filter(Jump)):
                states_to_remove.append(state)

        knowledge_base -= states_to_remove

        jumps_to_remove = []

        for jump in knowledge_base.filter(Jump):
            if (jump.state_from not in knowledge_base or
                jump.state_to not in knowledge_base):
                jumps_to_remove.append(jump)

        knowledge_base -= jumps_to_remove

        if not states_to_remove and not jumps_to_remove:
            break

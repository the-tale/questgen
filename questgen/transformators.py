# coding: utf-8

import random

from questgen import facts
from questgen import exceptions
from questgen.quests.base_quest import RESULTS


def activate_events(knowledge_base):
    choosen_facts = []
    removed_facts = []

    events = list(knowledge_base.filter(facts.Event))

    # chose events
    for event in events:
        event_facts = [knowledge_base[fact_uid] for fact_uid in event.members]

        if not event_facts:
            raise exceptions.NoEventMembersError(event=event)

        choosen_facts.append(random.choice(event_facts))
        removed_facts.extend(event_facts)

    knowledge_base -= set(removed_facts) - set(choosen_facts)


# here we MUST already have correct graph
def determine_default_choices(knowledge_base, preferred_markers=()):
    '''
    '''
    processed_choices = set()
    linked_options = {}
    restricted_options = set() # options, that can not be used as default
    preferred_markers = set(preferred_markers)

    for link in knowledge_base.filter(facts.OptionsLink):
        for option_uid in link.options:
            if option_uid in linked_options:
                raise exceptions.OptionWithTwoLinksError(option=knowledge_base[option_uid])
            linked_options[option_uid] = link

    for choice in knowledge_base.filter(facts.Choice):
        if choice.uid in processed_choices:
            continue

        processed_choices.add(choice.uid)

        options_choices = [option
                           for option in knowledge_base.filter(facts.Option)
                           if option.state_from == choice.uid and option.uid not in restricted_options]

        if not options_choices:
            # if there no valid options (in valuid graph), then all options where cancels by other chocices
            # and we will no go to that state by defaul states (quest author responded for this)
            # TODO: make restriction, that check if we have full default path
            continue

        filtered_options_choices = []

        if preferred_markers:
            filtered_options_choices = [candidate for candidate in options_choices if set(candidate.markers) & preferred_markers]

        if not filtered_options_choices:
            filtered_options_choices = options_choices

        default_option = random.choice(filtered_options_choices)

        if default_option.uid in linked_options:
            for linked_option_uid in linked_options[default_option.uid].options:
                if linked_option_uid == default_option.uid:
                    continue

                # option can be removed by other transformations
                if linked_option_uid not in knowledge_base:
                    continue

                linked_choice_uid = knowledge_base[linked_option_uid].state_from

                if linked_choice_uid in processed_choices:
                    raise exceptions.LinkedOptionWithProcessedChoiceError(option=knowledge_base[linked_option_uid])

                processed_choices.add(linked_choice_uid)

                knowledge_base += facts.ChoicePath(choice=linked_choice_uid, option=linked_option_uid, default=True)

        # if add all options linked to unused to restricted_options
        for unused_option in options_choices:
            if unused_option.uid == default_option.uid:
                continue
            if unused_option.uid not in linked_options:
                continue
            for linked_option_uid in linked_options[unused_option.uid].options:
                restricted_options.add(linked_option_uid)

        knowledge_base += facts.ChoicePath(choice=choice.uid, option=default_option.uid, default=True)


def change_choice(knowledge_base, new_option_uid, default):

    choice_uid = knowledge_base[new_option_uid].state_from

    knowledge_base -= [path for path in knowledge_base.filter(facts.ChoicePath) if path.choice == choice_uid]
    knowledge_base += facts.ChoicePath(choice=choice_uid, option=new_option_uid, default=default)

    links = [link for link in knowledge_base.filter(facts.OptionsLink) if new_option_uid in link.options]
    if links:
        link = links[0]
        for linked_option_uid in link.options:
            if new_option_uid == linked_option_uid:
                continue
            linked_choice_uid = knowledge_base[linked_option_uid].state_from

            knowledge_base -= [path for path in knowledge_base.filter(facts.ChoicePath) if path.choice == linked_choice_uid]
            knowledge_base += facts.ChoicePath(choice=linked_choice_uid, option=linked_option_uid, default=default)

    return True


def remove_broken_states(knowledge_base):

    # print '------------'
    # print [s.uid for s in knowledge_base.filter(facts.State)]
    # print '------------'

    knowledge_base -= list(knowledge_base.filter(facts.FakeFinish))

    while True:
        states_to_remove = set()

        for state in knowledge_base.filter(facts.State):
            if isinstance(state, facts.Start) and state.is_external:
                pass

            elif not [jump for jump in knowledge_base.filter(facts.Jump) if jump.state_to == state.uid]:
                states_to_remove.add(state)

            elif isinstance(state, facts.Finish) and state.is_external:
                pass

            elif isinstance(state, facts.Question):
                answers = [answer for answer in knowledge_base.filter(facts.Answer) if answer.state_from == state.uid]

                if len(answers) == 2:
                    if ( (answers[0].condition and not answers[1].condition) or
                         (not answers[0].condition and answers[1].condition) ):
                        continue

                states_to_remove.add(state)

            elif not [jump for jump in knowledge_base.filter(facts.Jump) if jump.state_from == state.uid]:
                states_to_remove.add(state)

        # print 'remove states', [s.uid for s in states_to_remove]
        knowledge_base -= states_to_remove

        jumps_to_remove = set()

        for jump in knowledge_base.filter(facts.Jump):
            if jump.state_from in knowledge_base and jump.state_to in knowledge_base:
                continue

            # print 'remove jump', jump.uid, (jump.state_from in knowledge_base), (jump.state_to in knowledge_base)
            jumps_to_remove.add(jump)

            if isinstance(jump, facts.Option):
                links = [l for l in knowledge_base.filter(facts.OptionsLink) if jump.uid in l.options]
                if links:
                    for link in links:
                        for option_uid in link.options:
                            # print 'remove linked jump', option_uid
                            jumps_to_remove.add(knowledge_base[option_uid])

        knowledge_base -= jumps_to_remove

        if not states_to_remove and not jumps_to_remove:
            break


def remove_restricted_states(knowledge_base):

    states_to_remove = set()

    for finish in knowledge_base.filter(facts.Finish):

        for restriction_fact in knowledge_base.filter(facts.OnlyGoodBranches):
            if finish.results.get(restriction_fact.object) not in (None, RESULTS.SUCCESSED):
                states_to_remove.add(finish)

        for restriction_fact in knowledge_base.filter(facts.OnlyBadBranches):
            if finish.results.get(restriction_fact.object) not in (None, RESULTS.FAILED):
                states_to_remove.add(finish)

        for restriction_fact in knowledge_base.filter(facts.ExceptBadBranches):
            if finish.results.get(restriction_fact.object) == RESULTS.FAILED:
                states_to_remove.add(finish)

        for restriction_fact in knowledge_base.filter(facts.ExceptGoodBranches):
            if finish.results.get(restriction_fact.object) == RESULTS.SUCCESSED:
                states_to_remove.add(finish)

    knowledge_base -= states_to_remove

    # print 'restricted states', [s.uid for s in states_to_remove]


def _get_actors(record):
    used_actors = set()

    for attribute_name, attribute in record._attributes.items():
        if attribute.is_reference:
            used_actors.add(getattr(record, attribute_name))

    return used_actors


def remove_unused_actors(knowledge_base):
    used_actors = set()

    for state in knowledge_base.filter(facts.State):
        for action in state.actions:
            used_actors |= _get_actors(action)

        for requirement in state.require:
            used_actors |= _get_actors(requirement)

        if isinstance(state, facts.Question):
            for condition in state.condition:
                used_actors |= _get_actors(condition)

    for participant in knowledge_base.filter(facts.QuestParticipant):
        used_actors |= _get_actors(participant)

    knowledge_base -= list(knowledge_base.filter(facts.Condition))
    knowledge_base -= list(knowledge_base.filter(facts.Restriction))

    # remove actors
    to_remove = set()
    for actor in knowledge_base.filter(facts.Actor):
        if actor.uid in used_actors:
            continue

        to_remove.add(actor)

    knowledge_base -= to_remove

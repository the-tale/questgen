# coding: utf-8

# TODO: tests
from questgen import facts

def percents_collector(knowledge_base):

    states_to_percents = {}

    for start in knowledge_base.filter(facts.Start):
        states_to_longest_path = {}
        processed_states = {}

        _persents_collector(knowledge_base=knowledge_base,
                            path=[start],
                            internal_quests=-1,
                            states_to_longest_path=states_to_longest_path,
                            processed_states=processed_states)

        longest_path = max(states_to_longest_path.values())

        for state_uid, is_internal in processed_states.items():
            if not is_internal:
                states_to_percents[state_uid] = 1.0 - float(states_to_longest_path[state_uid]) / longest_path

    return states_to_percents


def _update_longest_paths(path, paths, delta):
    for i, state in enumerate(reversed(path)):
        if state.uid not in paths or paths[state.uid] < i + delta:
            paths[state.uid] = i + delta


def _persents_collector(knowledge_base, path, internal_quests, states_to_longest_path, processed_states):

    if isinstance(path[-1], facts.Finish):
        if not internal_quests:
            _update_longest_paths(path, states_to_longest_path, 0)
            processed_states[path[-1].uid] = internal_quests
            return
        internal_quests -= 1

    elif isinstance(path[-1], facts.Start):
        internal_quests += 1

    for jump in (jump for jump in knowledge_base.filter(facts.Jump) if jump.state_from == path[-1].uid):
        if jump.state_from in processed_states:
            _update_longest_paths(path, states_to_longest_path, states_to_longest_path[jump.state_from])
            continue

        path.append(knowledge_base[jump.state_to])
        _persents_collector(knowledge_base, path, internal_quests, states_to_longest_path, processed_states)
        path.pop()

    processed_states[path[-1].uid] = internal_quests

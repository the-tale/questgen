# coding: utf-8

from questgen import facts

def get_absolute_start(knowledge_base):
    return next((start for start in knowledge_base.filter(facts.Start) if start.is_external))

def get_subquest_members(facts_list):
    return [f.uid for f in facts_list if isinstance(f, (facts.State, facts.Jump, facts.OptionsLink))]

def filter_subquest(facts_list, nesting):
    return (f for f in facts_list if isinstance(f, (facts.Start, facts.Finish)) and f.nesting == nesting + 1)


def get_required_interpreter_methods():
    from questgen import actions
    from questgen import requirements

    methods = ['on_state__before_actions',
               'on_state__after_actions',
               'on_jump_start__before_actions',
               'on_jump_start__after_actions',
               'on_jump_end__before_actions',
               'on_jump_end__after_actions']

    methods += [action._interpreter_do_method for action in actions.ACTIONS.values()]
    methods += [requirement._interpreter_check_method for requirement in requirements.REQUIREMENTS.values()]
    methods += [requirement._interpreter_satisfy_method for requirement in requirements.REQUIREMENTS.values()]

    return methods

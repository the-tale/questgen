# coding: utf-8

from questgen import facts

def get_absolute_start(knowledge_base):
    return (start for start in knowledge_base.filter(facts.Start) if start.is_external).next()

def get_subquest_members(facts_list):
    return [f.uid for f in facts_list if isinstance(f, (facts.State, facts.Jump, facts.OptionsLink))]

def filter_subquest(facts_list, nesting):
    return (f for f in facts_list if isinstance(f, (facts.Start, facts.Finish)) and f.nesting == nesting + 1)

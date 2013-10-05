# coding: utf-8

from questgen import facts

def get_absolute_start(knowledge_base):
    return (start for start in knowledge_base.filter(facts.Start) if start.is_entry).next()

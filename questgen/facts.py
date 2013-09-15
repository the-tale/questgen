# coding: utf-8

import copy

from questgen import exceptions

# Fact MUST be fully immutable (including deep relations)

######################
# Base class
######################

class Fact(object):
    _references = ()

    def __init__(self, uid=None, tags=(), label=None, description=None):
        self.uid = uid
        self.tags = tags
        self.label = label
        self.description = description

    def change(self, **kwargs):
        changed_fact = copy.deepcopy(self)
        for key, value in kwargs.items():
            if not hasattr(changed_fact, key):
                raise exceptions.WrongChangeAttributeError(fact=changed_fact, attribute=key)
            setattr(changed_fact, key, value)
        changed_fact.update_uid()
        return changed_fact

    def change_in_knowlege_base(self, knowledge_base, **kwargs):
        knowledge_base -= self
        knowledge_base += self.change(**kwargs)

    def check(self, knowledge_base):
        return self.uid in knowledge_base

    def update_uid(self):
        if self.uid is None:
            raise exceptions.UIDDidNotSetupped(fact=self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uid == other.uid

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return u'%s(uid="%s", tags="%s")' % (self.__class__.__name__, self.uid, self.tags)

######################
# Base classes for different knowlege aspects
######################

class Actor(Fact):

    def __init__(self, label='', **kwargs):
        super(Actor, self).__init__(**kwargs)
        self.label = label

    def __eq__(self, other):
        return super(Actor, self).__eq__(other)# and self.label == other.label


class State(Fact):

    def __init__(self, require=[], **kwargs):
        super(State, self).__init__(**kwargs)
        self.require = require

    def __eq__(self, other):
        return super(State, self).__eq__(other) and self.require == other.require

    def __repr__(self):
        return u'%s(uid="%s", require=%r, tags="%s")' % (self.__class__.__name__,
                                                         self.uid,
                                                         self.require,
                                                         self.tags)


class Jump(Fact):
    _references = ('state_from', 'state_to')

    def __init__(self, state_from, state_to, **kwargs):
        super(Jump, self).__init__(**kwargs)
        self.state_from = state_from
        self.state_to = state_to
        self.update_uid()

    def update_uid(self):
        self.uid='#jump<%s, %s>' % (self.state_from, self.state_to)

    def __eq__(self, other):
        return (super(Jump, self).__eq__(other) and
                self.state_from == other.state_from and
                self.state_to == other.state_to)

    def __repr__(self):
        return (u'Jump(state_from="%s", state_to="%s", tags="%s")' %
                (self.state_from, self.state_to, self.tags) )

class Condition(Fact):

    def __eq__(self, other):
        return super(Condition, self).__eq__(other)

class Pointer(Fact):
    UID = '#pointer'
    _references = ('state', 'jump')

    def __init__(self, state=None,  jump=None):
        super(Pointer, self).__init__(uid=self.UID)
        self.state = state
        self.jump = jump

    def __eq__(self, other):
        return (super(Pointer, self).__eq__(other) and
                self.state == other.state and
                self.jump == other.jump)

    def __repr__(self):
        return u'Pointer(state="%s", jump="%s", tags="%s")' % (self.state, self.jump, self.tags)


class Event(Fact):

    def __init__(self, tag, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.tag = tag
        self.update_uid()

    def update_uid(self):
        self.uid = '#event_%s' % self.tag

    def __eq__(self, other):
         return (super(Event, self).__eq__(other) and
                self.tag == other.tag)

    def __repr__(self):
        return u'Event(tag="%s", tags="%s")' % (self.tag, self.tags)


######################
# Concrete classes
######################


class Hero(Actor): pass
class Place(Actor): pass
class Person(Actor): pass


class Start(State):
    UID = '#start'

    def __init__(self, **kwargs):
        super(Start, self).__init__(uid=self.UID, **kwargs)

    def __repr__(self):
        return u'Start()'


class Finish(State): pass
class Choice(State): pass

class Option(Jump):

    def __init__(self, **kwargs):
        super(Option, self).__init__(**kwargs)

    def __eq__(self, other):
        return super(Option, self).__eq__(other)

    def __repr__(self):
        return (u'Option(state_from="%s", state_to="%s", tags="%s")' %
                (self.state_from, self.state_to, self.tags) )


class LocatedIn(Condition):
    _references = ('object', 'place')
    def __init__(self, object, place, **kwargs):
        super(LocatedIn, self).__init__(**kwargs)
        self.object = object
        self.place = place
        self.update_uid()

    def update_uid(self):
        self.uid = '#located_in<%s, %s>' % (self.object, self.place)


    @classmethod
    def relocate(cls, knowlege_base, object, new_place):
        location = filter(lambda fact: fact.object == object,
                          knowlege_base.filter(cls))[0]
        location.change_in_knowlege_base(knowlege_base, place=new_place)

    def __eq__(self, other):
        return (super(LocatedIn, self).__eq__(other) and
                self.object == other.object and
                self.place == other.place)

    def __repr__(self):
        return (u'LocatedIn(object="%s", place="%s", tags="%s")' %
                (self.object, self.place, self.tags) )

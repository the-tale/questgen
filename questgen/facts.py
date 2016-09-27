# coding: utf-8

from questgen import utils
from questgen import exceptions
from questgen import actions
from questgen import requirements
from questgen import records


class FactAttribute(records.RecordAttribute):
    __slots__ = ('is_uid', 'remove_in_short', 'is_serializable', 'deserialization_classes')

    def __init__(self, remove_in_short=False, deserialization_classes=None, is_uid=False, **kwargs):
        super(FactAttribute, self).__init__(**kwargs)
        self.is_uid = is_uid

        self.remove_in_short = remove_in_short

        self.is_serializable = deserialization_classes is not None
        self.deserialization_classes = deserialization_classes

    def need_serialization(self, value, short):
        if short and self.remove_in_short:
            return False
        if self.has_default and value == self.default:
            return False
        return True

    def serialize(self, value):
        if not self.is_serializable:
            return value

        return [object.serialize() for object in value]

    def deserialize(self, value):
        if not self.is_serializable:
            return value

        return [self.deserialization_classes[data['type']].deserialize(data) for data in value]


class FactMetaclass(records.RecordMetaclass):
    pass



class Fact(records.Record, metaclass=FactMetaclass):
    uid = FactAttribute(default=None)
    description = FactAttribute(remove_in_short=True, default=None)
    externals = FactAttribute(default=None)

    def __init__(self, **kwargs):
        super(Fact, self).__init__(**kwargs)
        self.update_uid()

    def serialize(self, short=False):
        return dict(type=self.type_name(),
                    attributes={name: self._attributes[name].serialize(getattr(self, name))
                                for name in self._attributes.keys()
                                if self._attributes[name].need_serialization(getattr(self, name), short=short)})

    @classmethod
    def deserialize(cls, data):
        attributes = {attribute_name: cls._attributes[attribute_name].deserialize(attribute_value)
                      for attribute_name, attribute_value in data['attributes'].items()
                      if attribute_name in cls._attributes}

        return cls(**attributes)


    def change(self, **kwargs):
        attributes = {attribute_name: getattr(self, attribute_name)
                      for attribute_name in self._attributes.keys()}

        for key in kwargs:
            if key not in attributes:
                raise exceptions.WrongChangeAttributeError(fact=self, attribute=key)

        attributes.update(kwargs)

        return self.__class__(**attributes)


    def change_in_knowlege_base(self, knowledge_base, **kwargs):
        knowledge_base -= self
        knowledge_base += self.change(**kwargs)

    def check(self, knowledge_base):
        return self.uid in knowledge_base

    def update_uid(self):
        if self.uid is None:
            uid_parts = []
            for attribute_name in sorted(self._attributes.keys()):
                attribute = self._attributes[attribute_name]
                if attribute.is_uid:
                    value = getattr(self, attribute_name)
                    if isinstance(value, (list, tuple)):
                        value = '|'.join(value)
                    uid_parts.append(str(value))

            self.uid = '#%s(%s)' % (utils.camel_to_underscores(self.type_name()), ', '.join(uid_parts))


######################
# Common Classes
######################

class Pointer(Fact):
    state = FactAttribute(is_reference=True, default=None)
    jump = FactAttribute(is_reference=True, default=None)


class Event(Fact):
    members = FactAttribute(default=())


class SubQuest(Fact):
    members = FactAttribute(default=())


######################
# Actor classes
######################

class Actor(Fact): pass

class Hero(Actor): pass

class Place(Actor):
    terrains = FactAttribute(default=None)
    type = FactAttribute(default=None)

class Person(Actor):
    profession = FactAttribute(default=None)

class Mob(Actor):
    terrains = FactAttribute(default=None)

######################
# States classes
######################

class State(Fact):
    require = FactAttribute(deserialization_classes=requirements.REQUIREMENTS, default=())
    actions = FactAttribute(deserialization_classes=actions.ACTIONS, default=())


class Jump(Fact):
    state_from = FactAttribute(is_reference=True, is_uid=True)
    state_to = FactAttribute(is_reference=True, is_uid=True)
    start_actions = FactAttribute(deserialization_classes=actions.ACTIONS, default=())
    end_actions = FactAttribute(deserialization_classes=actions.ACTIONS, default=())


class Start(State):
    type = FactAttribute()
    nesting = FactAttribute()

    @property
    def is_external(self): return self.nesting == 0

class Finish(State):
    nesting = FactAttribute()
    results = FactAttribute()
    start = FactAttribute(is_reference=True)

    @property
    def is_external(self): return self.nesting == 0


class FakeFinish(Finish):
    pass

#############
# Choice
#############

class Choice(State): pass


class Option(Jump):
    type = FactAttribute(is_uid=True)
    markers = FactAttribute()


class OptionsLink(Fact):
    options = FactAttribute(is_uid=True)


class ChoicePath(Fact):
    choice = FactAttribute(is_reference=True, is_uid=True)
    option = FactAttribute(is_reference=True, is_uid=True)
    default = FactAttribute(is_uid=True)

#############
# Question
#############

class Question(State):
    condition = FactAttribute(deserialization_classes=requirements.REQUIREMENTS)


class Answer(Jump):
    condition = FactAttribute(is_uid=True)


#############
# Conditions
#############

class Condition(Fact): pass

class SocialConnection(Condition):
    person_from = FactAttribute(is_reference=True, is_uid=True)
    person_to = FactAttribute(is_reference=True, is_uid=True)
    type = FactAttribute()

class LocatedIn(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)
    place = FactAttribute(is_reference=True, is_uid=True)


class LocatedNear(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)
    place = FactAttribute(is_reference=True, is_uid=True)
    terrains = FactAttribute(default=None)


class LocatedOnRoad(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)
    place_1 = FactAttribute(is_reference=True, is_uid=True)
    place_2 = FactAttribute(is_reference=True, is_uid=True)
    percents = FactAttribute()

    def check(self, knowledge_base):
        if self.uid not in knowledge_base:
            return False

        return self.percents < knowledge_base[self.uid].percents


class HasMoney(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)
    money = FactAttribute()

    def check(self, knowledge_base):
        if self.uid not in knowledge_base:
            return False

        return self.money <= knowledge_base[self.uid].money


class IsAlive(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)


class Preference(Condition):
    object = FactAttribute(is_reference=True, is_uid=True)


class PreferenceMob(Preference):
    mob = FactAttribute(is_reference=True, is_uid=True)


class PreferenceHometown(Preference):
    place = FactAttribute(is_reference=True, is_uid=True)


class PreferenceFriend(Preference):
    person = FactAttribute(is_reference=True, is_uid=True)


class PreferenceEnemy(Preference):
    person = FactAttribute(is_reference=True, is_uid=True)


class PreferenceEquipmentSlot(Preference):
    equipment_slot = FactAttribute(is_uid=True)


class QuestParticipant(Fact):
    participant = FactAttribute(is_reference=True, is_uid=True)
    role = FactAttribute(is_uid=True)
    start = FactAttribute(is_reference=True, is_uid=True)


class UpgradeEquipmentCost(Fact):
    money = FactAttribute(is_uid=True)


######################
# Restrictions classes
######################

class Restriction(Fact): pass

class OnlyGoodBranches(Restriction):
    object = FactAttribute(is_reference=True, is_uid=True)


class OnlyBadBranches(Restriction):
    object = FactAttribute(is_reference=True, is_uid=True)


class ExceptGoodBranches(Restriction):
    object = FactAttribute(is_reference=True, is_uid=True)


class ExceptBadBranches(Restriction):
    object = FactAttribute(is_reference=True, is_uid=True)


class NotFirstInitiator(Restriction):
    person = FactAttribute(is_reference=True, is_uid=True)


######################
# Markers classes
######################

class Marker(Fact): pass

class ProfessionMarker(Marker):
    person = FactAttribute(is_reference=True, is_uid=True)
    profession = FactAttribute(default=None)


FACTS = {fact_class.type_name(): fact_class
         for fact_class in list(globals().values())
         if isinstance(fact_class, type) and issubclass(fact_class, Fact)}

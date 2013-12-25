# coding: utf-8

from questgen import utils
from questgen import records


class ActionAttribute(records.RecordAttribute):
    pass


class ActionMetaclass(records.RecordMetaclass):

    def __new__(cls, name, bases, attributes):
        new_class = super(ActionMetaclass, cls).__new__(cls, name, bases, attributes)
        new_class._interpreter_do_method = 'do_%s' % utils.camel_to_underscores(name)
        return new_class


class Action(records.Record):
    __metaclass__ = ActionMetaclass

    def do(self, interpreter):
        return getattr(interpreter, self._interpreter_do_method)(action=self)


class Message(Action):
    type = ActionAttribute()


class GivePower(Action):
    object = ActionAttribute(is_reference=True)
    power = ActionAttribute()


class GiveReward(Action):
    object = ActionAttribute(is_reference=True)
    scale = ActionAttribute(default=1.0)
    type = ActionAttribute()


class Fight(Action):
    mercenary = ActionAttribute(default=None)
    mob = ActionAttribute(default=None)


class DoNothing(Action):
    type = ActionAttribute()


class UpgradeEquipment(Action):
    cost = ActionAttribute()


class MoveNear(Action):
    object = ActionAttribute(is_reference=True)
    place = ActionAttribute(is_reference=True, default=None)
    terrains = ActionAttribute(default=None)


class MoveIn(Action):
    object = ActionAttribute(is_reference=True)
    place = ActionAttribute(is_reference=True)
    percents = ActionAttribute()


ACTIONS = {action_class.type_name(): action_class
           for action_class in globals().values()
           if isinstance(action_class, type) and issubclass(action_class, Action) and action_class != Action}

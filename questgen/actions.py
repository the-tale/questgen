# coding: utf-8

from questgen import utils
from questgen import exceptions


class ActionAttribute(object):

    def __init__(self, is_reference=False, **kwargs):
        super(ActionAttribute, self).__init__()
        self.is_reference = is_reference
        self.has_default = 'default' in kwargs
        self.default = kwargs.get('default')


class _ActionMetaclass(type):

    def __new__(cls, name, bases, attributes):

        _references = []
        _attributes = {}

        action_attributes = {}

        for attribute_name, attribute in attributes.iteritems():
            if isinstance(attribute, ActionAttribute):
                _attributes[attribute_name] = attribute

                if attribute.is_reference:
                    _references.append(attribute_name)
            else:
                action_attributes[attribute_name] = attribute

        action_attributes['__slots__'] = tuple(attributes.keys())
        action_attributes['_references'] = tuple(_references)
        action_attributes['_attributes'] = _attributes
        action_attributes['_interpreter_method'] = 'do_%s' % utils.camel_to_underscores(name)

        return super(_ActionMetaclass, cls).__new__(cls, name, bases, action_attributes)


class Action(object):
    __metaclass__ = _ActionMetaclass

    def __init__(self, **kwargs):
        super(Action, self).__init__()
        for slot_attribute in self._attributes.iterkeys():
            if slot_attribute in kwargs:
                setattr(self, slot_attribute, kwargs[slot_attribute])
            elif self._attributes[slot_attribute].has_default:
                setattr(self, slot_attribute, self._attributes[slot_attribute].default)
            else:
                raise exceptions.RequiredActionAttributeError(action=self, attribute=slot_attribute)

        for name in kwargs.iterkeys():
            if name not in self._attributes:
                raise exceptions.WrongActionAttributeError(action=self, attribute=name)

    def serialize(self):
        return dict(type=self.type_name(),
                    attributes={name: getattr(self, name) for name in self._attributes.iterkeys()})

    @classmethod
    def deserialize(cls, data):
        return cls(**data['attributes'])

    @classmethod
    def type_name(cls): return cls.__name__

    def do(self, interpreter):
        return getattr(interpreter, self._interpreter_method)(**{attribute_name:getattr(self, attribute_name) for attribute_name in self._attributes.iterkeys()})


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
           if isinstance(action_class, type) and issubclass(action_class, Action)}

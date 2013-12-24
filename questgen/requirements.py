# coding: utf-8

from questgen import utils
from questgen import exceptions


class RequirementAttribute(object):

    def __init__(self, is_reference=False, **kwargs):
        super(RequirementAttribute, self).__init__()
        self.is_reference = is_reference
        self.has_default = 'default' in kwargs
        self.default = kwargs.get('default')


class _RequirementMetaclass(type):

    def __new__(cls, name, bases, attributes):

        _references = []
        _attributes = {}

        requirement_attributes = {}

        for attribute_name, attribute in attributes.iteritems():
            if isinstance(attribute, RequirementAttribute):
                _attributes[attribute_name] = attribute

                if attribute.is_reference:
                    _references.append(attribute_name)
            else:
                requirement_attributes[attribute_name] = attribute

        requirement_attributes['__slots__'] = tuple(attributes.keys())
        requirement_attributes['_references'] = tuple(_references)
        requirement_attributes['_attributes'] = _attributes
        requirement_attributes['_checker_method'] = 'check_%s' % utils.camel_to_underscores(name)

        return super(_RequirementMetaclass, cls).__new__(cls, name, bases, requirement_attributes)


class Requirement(object):
    __metaclass__ = _RequirementMetaclass

    def __init__(self, **kwargs):
        super(Requirement, self).__init__()
        for slot_attribute in self._attributes.iterkeys():
            if slot_attribute in kwargs:
                setattr(self, slot_attribute, kwargs[slot_attribute])
            elif self._attributes[slot_attribute].has_default:
                setattr(self, slot_attribute, self._attributes[slot_attribute].default)
            else:
                raise exceptions.RequiredRequirementAttributeError(requirement=self, attribute=slot_attribute)

        for name in kwargs.iterkeys():
            if name not in self._attributes:
                raise exceptions.WrongRequirementAttributeError(requirement=self, attribute=name)

    def serialize(self):
        return dict(type=self.type_name(),
                    attributes={name: getattr(self, name) for name in self._attributes.iterkeys()})

    @classmethod
    def deserialize(cls, data):
        return cls(**data['attributes'])

    @classmethod
    def type_name(cls): return cls.__name__

    def check(self, requirement_checker):
        return getattr(requirement_checker, self._checker_method)(**{attribute_name:getattr(self, attribute_name) for attribute_name in self._attributes.iterkeys()})


class LocatedIn(Requirement):
    object = RequirementAttribute(is_reference=True)
    place = RequirementAttribute(is_reference=True)


class LocatedNear(Requirement):
    object = RequirementAttribute(is_reference=True)
    place = RequirementAttribute(is_reference=True)


class LocatedOnRoad(Requirement):
    object = RequirementAttribute(is_reference=True)
    place_1 = RequirementAttribute(is_reference=True)
    place_2 = RequirementAttribute(is_reference=True)
    percents = RequirementAttribute(default=None)


class HasMoney(Requirement):
    object = RequirementAttribute(is_reference=True)
    money = RequirementAttribute()


class IsAlive(Requirement):
    object = RequirementAttribute(is_reference=True)


REQUIREMENTS = {requirement_class.type_name(): requirement_class
                for requirement_class in globals().values()
                if isinstance(requirement_class, type) and issubclass(requirement_class, Requirement)}

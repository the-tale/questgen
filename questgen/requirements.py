# coding: utf-8

from questgen import utils
from questgen import records


class RequirementAttribute(records.RecordAttribute):
    pass


class RequirementMetaclass(records.RecordMetaclass):

    def __new__(cls, name, bases, attributes):
        new_class = super(RequirementMetaclass, cls).__new__(cls, name, bases, attributes)

        new_class._interpreter_check_method = 'check_%s' % utils.camel_to_underscores(name)
        new_class._interpreter_satisfy_method = 'satisfy_%s' % utils.camel_to_underscores(name)

        return new_class


class Requirement(records.Record, metaclass=RequirementMetaclass):
    def check(self, requirement_checker):
        return getattr(requirement_checker, self._interpreter_check_method)(requirement=self)

    def satisfy(self, requirement_checker):
        return getattr(requirement_checker, self._interpreter_satisfy_method)(requirement=self)


class LocatedIn(Requirement):
    object = RequirementAttribute(is_reference=True)
    place = RequirementAttribute(is_reference=True)


class LocatedNear(Requirement):
    object = RequirementAttribute(is_reference=True)
    place = RequirementAttribute(is_reference=True)
    terrains = RequirementAttribute(default=None)


class LocatedOnRoad(Requirement):
    object = RequirementAttribute(is_reference=True)
    place_from = RequirementAttribute(is_reference=True)
    place_to = RequirementAttribute(is_reference=True)
    percents = RequirementAttribute(default=None)


class HasMoney(Requirement):
    object = RequirementAttribute(is_reference=True)
    money = RequirementAttribute()


class IsAlive(Requirement):
    object = RequirementAttribute(is_reference=True)


REQUIREMENTS = {requirement_class.type_name(): requirement_class
                for requirement_class in list(globals().values())
                if isinstance(requirement_class, type) and issubclass(requirement_class, Requirement) and requirement_class != Requirement}

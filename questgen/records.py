# coding: utf-8

from questgen import exceptions


class RecordAttribute(object):
    __slots__ = ('is_reference', 'has_default', 'default')

    def __init__(self, is_reference=False, **kwargs):
        super(RecordAttribute, self).__init__()
        self.is_reference = is_reference

        self.has_default = 'default' in kwargs
        self.default = kwargs.get('default')




class RecordMetaclass(type):

    def __new__(cls, name, bases, attributes):

        _references = set()
        _attributes = {}

        for base in bases:
            if isinstance(base, RecordMetaclass):
                _attributes.update(base._attributes)
                _references |= base._references

        record_attributes = {}

        for attribute_name, attribute in attributes.items():
            if isinstance(attribute, RecordAttribute):
                _attributes[attribute_name] = attribute

                if attribute.is_reference:
                    _references.add(attribute_name)
            else:
                record_attributes[attribute_name] = attribute

        record_attributes['__slots__'] = tuple(_attributes.keys())
        record_attributes['_references'] = _references
        record_attributes['_attributes'] = _attributes

        return super(RecordMetaclass, cls).__new__(cls, name, bases, record_attributes)


class Record(object, metaclass=RecordMetaclass):
    def __init__(self, **kwargs):
        super(Record, self).__init__()
        for slot_attribute in self._attributes.keys():
            if slot_attribute in kwargs:
                setattr(self, slot_attribute, kwargs[slot_attribute])
            elif self._attributes[slot_attribute].has_default:
                setattr(self, slot_attribute, self._attributes[slot_attribute].default)
            else:
                raise exceptions.RequiredRecordAttributeError(record=self, attribute=slot_attribute)

        for name in kwargs.keys():
            if name not in self._attributes:
                raise exceptions.WrongRecordAttributeError(record=self, attribute=name)


    def serialize(self):
        return dict(type=self.type_name(),
                    attributes={name: getattr(self, name) for name in self._attributes.keys()})

    @classmethod
    def deserialize(cls, data):
        return cls(**data['attributes'])

    def __eq__(self, other):
        return self.__class__ == other.__class__ and all(getattr(self, attribute) == getattr(other, attribute) for attribute in self._attributes.keys())

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.__class__) # bad implementaion, but fast

    @classmethod
    def type_name(cls): return cls.__name__

    def __repr__(self):
        return '%s(%s)' % (self.type_name(),
                            ', '.join('%s=%r' % (attribute, getattr(self, attribute))
                                       for attribute, default in sorted(self._attributes.items())
                                       if hasattr(self, attribute) and getattr(self, attribute) != default))

# coding: utf-8

from questgen import exceptions


class RecordAttribute(object):

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

        for attribute_name, attribute in attributes.iteritems():
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


class Record(object):
    __metaclass__ = RecordMetaclass

    def __init__(self, **kwargs):
        super(Record, self).__init__()
        for slot_attribute in self._attributes.iterkeys():
            if slot_attribute in kwargs:
                setattr(self, slot_attribute, kwargs[slot_attribute])
            elif self._attributes[slot_attribute].has_default:
                setattr(self, slot_attribute, self._attributes[slot_attribute].default)
            else:
                raise exceptions.RequiredRecordAttributeError(record=self, attribute=slot_attribute)

        for name in kwargs.iterkeys():
            if name not in self._attributes:
                raise exceptions.WrongRecordAttributeError(record=self, attribute=name)


    def serialize(self):
        return dict(type=self.type_name(),
                    attributes={name: getattr(self, name) for name in self._attributes.iterkeys()})

    @classmethod
    def deserialize(cls, data):
        return cls(**data['attributes'])

    def __eq__(self, other):
        return self.__class__ == other.__class__ and all(getattr(self, attribute) == getattr(other, attribute) for attribute in self._attributes.iterkeys())

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def type_name(cls): return cls.__name__

    def __repr__(self):
        return u'%s(%s)' % (self.type_name(),
                            u', '.join(u'%s=%r' % (attribute, getattr(self, attribute))
                                       for attribute, default in self._attributes.iteritems()
                                       if hasattr(self, attribute) and getattr(self, attribute) != default))

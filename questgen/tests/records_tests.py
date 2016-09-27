# coding: utf-8

import unittest

from questgen import records
from questgen import exceptions


class ParentRecord(records.Record, metaclass=records.RecordMetaclass):
    attr_1 = records.RecordAttribute()
    attr_2 = records.RecordAttribute(is_reference=True, default=None)


class ChildRecord(ParentRecord):
    attr_3 = records.RecordAttribute(is_reference=True)



class RecordsTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_slots(self):
        self.assertTrue('attr_1' in ChildRecord.__slots__)
        self.assertTrue('attr_2' in ChildRecord.__slots__)
        self.assertTrue('attr_3' in ChildRecord.__slots__)

    def test_attributes(self):
        self.assertTrue('attr_1' in ChildRecord._attributes)
        self.assertTrue('attr_2' in ChildRecord._attributes)
        self.assertTrue('attr_3' in ChildRecord._attributes)

    def test_references(self):
        self.assertFalse('attr_1' in ChildRecord._references)
        self.assertTrue('attr_2' in ChildRecord._references)
        self.assertTrue('attr_3' in ChildRecord._references)

    def test__serialization(self):
        record = ChildRecord(attr_1=1, attr_3=666)
        self.assertEqual(record.serialize(), ChildRecord.deserialize(record.serialize()).serialize())

    def test_required_attribute_error(self):
        self.assertRaises(exceptions.RequiredRecordAttributeError, ChildRecord, attr_1=1)

    def test_wrong_attribute_error(self):
        self.assertRaises(exceptions.WrongRecordAttributeError, ChildRecord, attr_1=1, attr_3=3, attr_4=1)

    def test_eq(self):
        record_1 = ChildRecord(attr_1=1, attr_3=666)
        record_2 = ChildRecord(attr_1=1, attr_3=666)
        record_3 = ChildRecord(attr_1=1, attr_3=666, attr_2=7)
        self.assertTrue(record_1 == record_2)
        self.assertFalse(record_1 == record_3)

    def test_ne(self):
        record_1 = ChildRecord(attr_1=1, attr_3=666)
        record_2 = ChildRecord(attr_1=1, attr_3=666)
        record_3 = ChildRecord(attr_1=1, attr_3=666, attr_2=7)
        self.assertFalse(record_1 != record_2)
        self.assertTrue(record_1 != record_3)

    def test_type_name(self):
        self.assertEqual(ChildRecord.type_name(), 'ChildRecord')

    def test_repr(self):
        self.assertEqual(ChildRecord(attr_1=1, attr_3=666).__repr__(), 'ChildRecord(attr_1=1, attr_2=None, attr_3=666)')

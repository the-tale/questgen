# coding: utf-8

class ROLES(object):
    INITIATOR = 'initiator'
    INITIATOR_POSITION = 'initiator_position'
    RECEIVER = 'receiver'
    RECEIVER_POSITION = 'receiver_position'


class BaseQuest(object):
    UID = None
    TAGS = ()

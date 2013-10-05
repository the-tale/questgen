# coding: utf-8

class ROLES(object):
    INITIATOR = 'initiator'
    INITIATOR_POSITION = 'initiator_position'
    RECEIVER = 'receiver'
    RECEIVER_POSITION = 'receiver_position'

    ANTAGONIST = 'antagonist'
    ANTAGONIST_POSITION = 'antagonist_position'


class RESULTS(object):
    SUCCESSED = 'successed'
    FAILED = 'failed'


class BaseQuest(object):
    TYPE = None
    TAGS = ()


class QuestBetween2(BaseQuest):

    @classmethod
    def construct_from_nothing(cls, selector):
        return cls.construct_from_place(selector=selector, start_place=selector.new_place())

    @classmethod
    def construct_from_place(cls, selector, start_place):
        return cls.construct_between_2(selector,
                                       initiator=selector.person_from(places=(start_place.uid, )),
                                       receiver=selector.new_person())

    @classmethod
    def construct_from_person(cls, selector, initiator):
        return cls.construct_between_2(selector, initiator, receiver=selector.new_person())

    @classmethod
    def construct_between_2(cls, selector, initiator, receiver):
        return cls.construct( selector,
                              initiator=initiator,
                              initiator_position=selector.place_for(objects=(initiator.uid,)),
                              receiver=receiver,
                              receiver_position=selector.place_for(objects=(receiver.uid,)))

    @classmethod
    def construct(cls, selector, initiator, initiator_position, receiver, receiver_position):
        raise NotImplementedError

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
    NEUTRAL = 'neutral'
    FAILED = 'failed'


class BaseQuest(object):
    TYPE = None
    TAGS = ()


class QuestBetween2(BaseQuest):

    @classmethod
    def find_receiver(cls, selector, initiator):
        raise NotImplementedError()

    @classmethod
    def construct_from_nothing(cls, nesting, selector):
        return cls.construct_from_place(nesting=nesting, selector=selector, start_place=selector.new_place())

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):
        initiator = selector.new_person(first_initiator=(nesting==0), restrict_places=False, places=(start_place.uid, ))
        return cls.construct_between_2(nesting=nesting,
                                       selector=selector,
                                       initiator=initiator,
                                       receiver=cls.find_receiver(selector=selector, initiator=initiator))

    @classmethod
    def construct_from_person(cls, nesting, selector, initiator):
        return cls.construct_between_2(nesting=nesting,
                                       selector=selector,
                                       initiator=initiator,
                                       receiver=cls.find_receiver(selector=selector, initiator=initiator))

    @classmethod
    def construct_between_2(cls, nesting, selector, initiator, receiver):
        return cls.construct( nesting=nesting,
                              selector=selector,
                              initiator=initiator,
                              initiator_position=selector.place_for(objects=(initiator.uid,)),
                              receiver=receiver,
                              receiver_position=selector.place_for(objects=(receiver.uid,)))

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):
        raise NotImplementedError

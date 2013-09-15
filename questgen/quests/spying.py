# coding: utf-8

from questgen.quests.base_quest import BaseQuest
from questgen import selectors
from questgen.facts import ( Start,
                             State,
                             Jump,
                             Finish,
                             Event,
                             Place,
                             Person,
                             LocatedIn,
                             LocatedNear,
                             Choice,
                             Option,
                             Message)


class Spying(BaseQuest):
    UID = 'spying'
    TAGS = ('normal', 'can_start', 'can_continue')

    # normal - normal quest
    # special - special quest
    # can_start - can be first quest in tree
    # can_continue - can be not first quest in tree

    @classmethod
    def construct_from_nothing(cls, selector):
        return cls.construct_from_place(selector, selector.new_place())

    @classmethod
    def construct_from_place(cls, selector, start_place):
        return cls.construct_between_2(selector,
                                       initiator=selector.person_from(places=(start_place, )),
                                       receiver=selector.new_person())

    @classmethod
    def construct_from_person(cls, selector, initiator):
        return cls.construct_between_2(selector, initiator, receiver=selector.new_person())

    @classmethod
    def construct_between_2(cls, selector, initiator, receiver):
        return cls.construct(selector,
                              initiator=initiator,
                              initiator_position=selector.place_for(objects=(initiator,)),
                              receiver=receiver,
                              receiver_position=selector.place_for(objects=(receiver,)))

    @classmethod
    def construct(cls, selector, initiator, initiator_position, receiver, receiver_position):

        hero_uid = selector.heroes()[0].uid

        facts = [ Start(label=u'Начало',
                        description=u'Задание на шпионаж',
                        require=[LocatedIn(object=hero_uid, place=initiator_position),
                                 LocatedIn(object=receiver, place=receiver_position)],
                        actions=[Message(id='intro')]),

                  Jump(state_from=Start.UID, state_to='arrived_to_target'),
                  State(uid='arrived_to_target',
                        label=u'Прибытие в город цели',
                        description=u'Герой путешествует к месту жительства цели',
                        require=[LocatedIn(object=hero_uid, place=receiver_position)],
                        actions=[Message(id='arrived_to_target')]),

                  Jump(state_from='arrived_to_target', state_to='start_spying'),
                  Choice(uid='start_spying',
                         label=u'Шпионаж',
                         description=u'герой отправляется шпионить',
                         actions=[Message(id='start_spying'),
                                  LocatedNear(object=hero_uid, place=receiver_position)]),
                  Option(state_from='start_spying', state_to='continue_spying'),
                  Option(state_from='start_spying', state_to='open_up'),

                  State(uid='continue_spying',
                        label=u'Продолжить шпионаж',
                        description=u'Герой шпионит за целью',
                        actions=[Message(id='continue_spying'),
                                 LocatedNear(object=hero_uid, place=receiver_position)]),
                  State(uid='open_up',
                        label=u'Раскрыться',
                        description=u'Сообщить цели о шпионаже',
                        actions=[Message(id='open_up')]),

                  Jump(state_from='continue_spying', state_to='report_data'),
                  Finish(uid='report_data',
                         label=u'Сообщить сообранную информацию',
                         description=u'Вернуться к нанивателю и сообщить собранную информацию',
                         require=[LocatedIn(object=hero_uid, place=initiator_position)],
                         actions=[Message(id='report_data')]),

                  Event(tag='open_up_variants', label=u'Варианты окончания раскрытия'),

                  Finish(uid='open_up_finish',
                         label=u'Завершить задаие',
                         description=u'Завершить задание и остатсья в городе цели',
                         tags=('open_up_variants',),
                         require=[LocatedIn(object=hero_uid, place=receiver_position)],
                         actions=[Message(id='open_up_finish')]),
                  Finish(uid='open_up_lying',
                         label=u'Обмануть заказчика',
                         description=u'Вернуться к заказчику и сообщить ложную информацию',
                         tags=('open_up_variants',),
                         require=[LocatedIn(object=hero_uid, place=initiator_position)],
                         actions=[Message(id='open_up_lying')]),

                  Jump(state_from='open_up', state_to='open_up_finish'),
                  Jump(state_from='open_up', state_to='open_up_lying'),
              ]

        return facts

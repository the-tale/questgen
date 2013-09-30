# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES
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
                             Message,
                             GivePower,
                             OptionsLink,
                             QuestParticipant)


class Spying(QuestBetween2):
    TYPE = 'spying'
    TAGS = ('can_start', 'can_continue')

    # normal - normal quest
    # special - special quest
    # can_start - can be first quest in tree
    # can_continue - can be not first quest in tree

    @classmethod
    def construct(cls, knowledge_base, selector, initiator, initiator_position, receiver, receiver_position):

        hero_uid = selector.heroes()[0]

        ns = knowledge_base.get_next_ns()

        open_up_variants = Event(uid=ns+'open_up_variants', description=u'Варианты окончания раскрытия')

        start = Start(uid=ns+'start',
                      type=cls.TYPE,
                      description=u'Начало: задание на шпионаж',
                      require=[LocatedIn(object=hero_uid, place=initiator_position),
                               LocatedIn(object=receiver, place=receiver_position)],
                      actions=[Message(id='intro')])

        participants = [QuestParticipant(start=start.uid, participant=initiator, role=ROLES.INITIATOR),
                        QuestParticipant(start=start.uid, participant=receiver, role=ROLES.RECEIVER) ]

        start_spying = Choice(uid=ns+'start_spying',
                              description=u'Прибытие в город цели',
                              require=[LocatedIn(object=hero_uid, place=receiver_position)],
                              actions=[Message(id='arrived_to_target')])


        spying_middle = Choice(uid=ns+'spying_middle',
                               description=u'Шпионаж',
                               actions=[LocatedNear(object=hero_uid, place=receiver_position)])

        continue_spying = State(uid=ns+'continue_spying',
                                description=u'Продолжить шпионаж',
                                require=[LocatedNear(object=hero_uid, place=receiver_position)],
                                actions=[LocatedNear(object=hero_uid, place=receiver_position),
                                         Message(id='continue_spying')])

        open_up = State(uid=ns+'open_up',
                        description=u'Раскрыться',
                        require=[LocatedIn(object=hero_uid, place=receiver_position)],
                        actions=[Message(id='open_up')])


        report_data = Finish(uid=ns+'report_data',
                             type='report_data',
                             description=u'Сообщить сообранную информацию',
                             require=[LocatedIn(object=hero_uid, place=initiator_position)],
                             actions=[Message(id='report_data'),
                                      GivePower(object=initiator, power=1),
                                      GivePower(object=receiver, power=-1)])

        open_up_finish = Finish(uid=ns+'open_up_finish',
                                type='open_up_finish',
                                description=u'Завершить задание и остатсья в городе цели',
                                tags=(open_up_variants.uid,),
                                require=[LocatedIn(object=hero_uid, place=receiver_position)],
                                actions=[Message(id='open_up_finish'),
                                      GivePower(object=initiator, power=-1),
                                      GivePower(object=receiver, power=1)])

        open_up_lying = Finish(uid=ns+'open_up_lying',
                               type='open_up_lying',
                               description=u'Вернуться к заказчику и сообщить ложную информацию',
                               tags=(open_up_variants.uid,),
                               require=[LocatedIn(object=hero_uid, place=initiator_position)],
                               actions=[Message(id='open_up_lying'),
                                        GivePower(object=initiator, power=-1),
                                        GivePower(object=receiver, power=1)])

        start_spying__spying_middle = Option(state_from=start_spying.uid, state_to=spying_middle.uid, type='spy', start_actions=[Message(id='start_spying'),])
        start_spying__open_up = Option(state_from=start_spying.uid, state_to=open_up.uid, type='open_up', start_actions=[Message(id='start_open_up'),])

        spying_middle__continue_spying = Option(state_from=spying_middle.uid, state_to=continue_spying.uid, type='spy')
        spying_middle__open_up = Option(state_from=spying_middle.uid, state_to=open_up.uid, type='open_up', start_actions=[Message(id='start_open_up'),])


        facts = [ start,
                  start_spying,
                  spying_middle,
                  continue_spying,
                  open_up,
                  report_data,
                  open_up_finish,
                  open_up_lying,

                  Jump(state_from=start.uid, state_to=start_spying.uid),

                  start_spying__spying_middle,
                  start_spying__open_up,

                  spying_middle__continue_spying,
                  spying_middle__open_up,

                  Jump(state_from=continue_spying.uid, state_to=report_data.uid, start_actions=[Message(id='move_to_report_data'),]),

                  Jump(state_from=open_up.uid, state_to=open_up_finish.uid),
                  Jump(state_from=open_up.uid, state_to=open_up_lying.uid, start_actions=[Message(id='move_to_report_lie'),]),

                  OptionsLink(options=(start_spying__open_up.uid, spying_middle__open_up.uid)),
                  OptionsLink(options=(start_spying__spying_middle.uid, spying_middle__continue_spying.uid)),

                  open_up_variants
                ]

        facts.extend(participants)

        return facts

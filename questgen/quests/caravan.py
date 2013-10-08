# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class Caravan(QuestBetween2):
    TYPE = 'caravan'
    TAGS = ('can_start', 'can_continue')

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        black_market = selector.new_place()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description=u'Начало: караван',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=black_market.uid, role=ROLES.ANTAGONIST_POSITION)]

        first_moving = facts.State(uid=ns+'first_moving',
                                    description=u'двигаемся с караваном',
                                    actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.3), ))

        caravan_choice = facts.Choice(uid=ns+'caravan_choice',
                                      description=u'Решение: защитить или ограбить')

        first_defence = facts.Choice(uid=ns+'first_defence',
                                     description=u'первая защита',
                                     actions=(facts.Message(type='defence'),
                                              facts.Fight(uid='fight_1'), ))

        second_moving = facts.State(uid=ns+'second_moving',
                                    description=u'двигаемся с караваном',
                                    actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.6), ))

        second_defence = facts.State(uid=ns+'second_defence',
                                     description=u'вторая защита',
                                     actions=(facts.Message(type='defence'),
                                              facts.Fight(uid='fight_2'), ))

        finish_defence = facts.Finish(uid=ns+'finish_defence',
                                      result=RESULTS.SUCCESSED,
                                      nesting=nesting,
                                      description=u'Караван приходит в точку назначения',
                                      require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                      actions=[facts.GiveReward(object=hero.uid, type='finish_defence'),
                                               facts.GivePower(object=initiator.uid, power=1),
                                               facts.GivePower(object=receiver.uid, power=1)])

        move_to_attack = facts.State(uid=ns+'move_to_attack',
                                    description=u'ведём караван в засаду',
                                    actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.5), ))

        attack = facts.State(uid=ns+'attack',
                             description=u'нападение',
                             actions=(facts.Message(type='attack'),
                                      facts.Fight(uid='fight_3'), ))

        run = facts.State(uid=ns+'run',
                          description=u'скрываемся с места преступления',
                          actions=(facts.MoveNear(object=hero.uid),))

        fight = facts.State(uid=ns+'fight',
                            description=u'защита награбленного',
                            actions=(facts.Message(type='fight'),
                                     facts.Fight(uid='fight_4'), ))

        hide = facts.State(uid=ns+'hide',
                           description=u'прячемся',
                           actions=(facts.Message(type='hide'),
                                    facts.MoveNear(object=hero.uid)))

        finish_attack = facts.Finish(uid=ns+'finish_attack',
                                     result=RESULTS.FAILED,
                                     nesting=nesting,
                                     description=u'Продать товар на чёрном рынке',
                                     require=[facts.LocatedIn(object=hero.uid, place=black_market.uid)],
                                     actions=[facts.GiveReward(object=hero.uid, type='finish_attack'),
                                              facts.GivePower(object=initiator.uid, power=-1),
                                              facts.GivePower(object=receiver.uid, power=-1),
                                              facts.GivePower(object=black_market.uid, power=1)])

        caravan_choice__first_defence = facts.Option(state_from=caravan_choice.uid, state_to=first_defence.uid,
                                                     type='jump_defence', start_actions=[facts.Message(type='choose_defence'),])
        caravan_choice__move_to_attack = facts.Option(state_from=caravan_choice.uid, state_to=move_to_attack.uid,
                                                      type='jump_attack', start_actions=[facts.Message(type='choose_attack'),])

        first_defence__second_moving = facts.Option(state_from=first_defence.uid, state_to=second_moving.uid,
                                                     type='jump_defence', start_actions=[facts.Message(type='choose_defence'),])
        first_defence__move_to_attack = facts.Option(state_from=first_defence.uid, state_to=move_to_attack.uid,
                                             type='jump_attack', start_actions=[facts.Message(type='choose_attack'),])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=first_moving.uid, start_actions=(facts.Message(type='first_moving'), )),

                 first_moving,

                 facts.Jump(state_from=first_moving.uid, state_to=caravan_choice.uid),

                 caravan_choice,

                 caravan_choice__first_defence,
                 caravan_choice__move_to_attack,

                 first_defence,

                 first_defence__second_moving,
                 first_defence__move_to_attack,

                 second_moving,

                 facts.Jump(state_from=second_moving.uid, state_to=second_defence.uid),

                 second_defence,

                 facts.Jump(state_from=second_defence.uid, state_to=finish_defence.uid),

                 finish_defence,

                 move_to_attack,

                 facts.Jump(state_from=move_to_attack.uid, state_to=attack.uid),

                 attack,

                 facts.Jump(state_from=attack.uid, state_to=run.uid, start_actions=(facts.Message(type='start_run'),)),

                 run,

                 facts.Jump(state_from=run.uid, state_to=fight.uid),

                 fight,

                 facts.Jump(state_from=fight.uid, state_to=hide.uid, start_actions=(facts.Message(type='start_hide'),)),

                 hide,

                 facts.Jump(state_from=hide.uid, state_to=finish_attack.uid),

                 finish_attack,

                 facts.OptionsLink(options=(caravan_choice__first_defence.uid, first_defence__second_moving.uid)),
                ]

        line.extend(participants)

        return line

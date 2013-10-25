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
                                    actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.2), ))

        caravan_choice = facts.Choice(uid=ns+'caravan_choice',
                                      description=u'Решение: защитить или ограбить')

        first_defence = facts.Choice(uid=ns+'first_defence',
                                     description=u'первая защита',
                                     actions=(facts.Message(type='defence'),
                                              facts.Fight(uid='fight_1'), ))

        first_defence_continue = facts.Question(uid=ns+'first_defence_continue',
                                                description=u'удалось ли защитить караван?',
                                                condition=(facts.IsAlive(object=hero.uid),))

        second_moving = facts.State(uid=ns+'second_moving',
                                    description=u'двигаемся с караваном',
                                    actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.5), ))

        second_defence = facts.Question(uid=ns+'second_defence',
                                        description=u'вторая защита',
                                        condition=(facts.IsAlive(object=hero.uid),),
                                        actions=(facts.Message(type='defence'),
                                                 facts.Fight(uid='fight_2'), ))

        finish_defence = facts.Finish(uid=ns+'finish_defence',
                                      start=start.uid,
                                      results={ initiator.uid: RESULTS.SUCCESSED,
                                                receiver.uid: RESULTS.SUCCESSED,
                                                black_market.uid: RESULTS.NEUTRAL },
                                      nesting=nesting,
                                      description=u'Караван приходит в точку назначения',
                                      require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                      actions=[facts.GiveReward(object=hero.uid, type='finish_defence'),
                                               facts.GivePower(object=initiator.uid, power=1),
                                               facts.GivePower(object=receiver.uid, power=1)])

        move_to_attack = facts.State(uid=ns+'move_to_attack',
                                     description=u'ведём караван в засаду',
                                     actions=(facts.MoveIn(object=hero.uid, place=receiver_position.uid, percents=0.3), ))

        attack = facts.Question(uid=ns+'attack',
                                description=u'нападение',
                                condition=(facts.IsAlive(object=hero.uid),),
                                actions=(facts.Message(type='attack'),
                                         facts.Fight(uid='fight_3', mercenary=True), ))

        run = facts.State(uid=ns+'run',
                          description=u'скрываемся с места преступления',
                          actions=(facts.MoveNear(object=hero.uid),))

        fight = facts.Question(uid=ns+'fight',
                               description=u'защита награбленного',
                               condition=(facts.IsAlive(object=hero.uid),),
                               actions=(facts.Message(type='fight'),
                                        facts.Fight(uid='fight_4', mercenary=True), ))

        hide = facts.State(uid=ns+'hide',
                           description=u'прячемся',
                           actions=(facts.Message(type='hide'),
                                    facts.MoveNear(object=hero.uid)))

        finish_attack = facts.Finish(uid=ns+'finish_attack',
                                     start=start.uid,
                                     results={ initiator.uid: RESULTS.FAILED,
                                               receiver.uid: RESULTS.FAILED,
                                               black_market.uid: RESULTS.SUCCESSED },
                                     nesting=nesting,
                                     description=u'Продать товар на чёрном рынке',
                                     require=[facts.LocatedIn(object=hero.uid, place=black_market.uid)],
                                     actions=[facts.GiveReward(object=hero.uid, type='finish_attack'),
                                              facts.GivePower(object=initiator.uid, power=-1),
                                              facts.GivePower(object=receiver.uid, power=-1),
                                              facts.GivePower(object=black_market.uid, power=1)])

        finish_defence_failed = facts.Finish(uid=ns+'finish_defence_failed',
                                             start=start.uid,
                                             results={ initiator.uid: RESULTS.FAILED,
                                                       receiver.uid: RESULTS.FAILED,
                                                       black_market.uid: RESULTS.NEUTRAL },
                                             nesting=nesting,
                                             description=u'Герой не смог защитить караван',
                                             require=[facts.LocatedIn(object=hero.uid, place=black_market.uid)],
                                             actions=[facts.Message(type='finish_defence_failed'),
                                                      facts.GivePower(object=initiator.uid, power=-1),
                                                      facts.GivePower(object=receiver.uid, power=-1)])

        finish_attack_failed = facts.Finish(uid=ns+'finish_attack_failed',
                                            start=start.uid,
                                            results={ initiator.uid: RESULTS.SUCCESSED,
                                                      receiver.uid: RESULTS.SUCCESSED,
                                                      black_market.uid: RESULTS.NEUTRAL },
                                            nesting=nesting,
                                            description=u'Герой не смог ограбить караван',
                                            require=[facts.LocatedIn(object=hero.uid, place=black_market.uid)],
                                            actions=[facts.Message(type='finish_attack_failed'),
                                                     facts.GivePower(object=initiator.uid, power=1),
                                                     facts.GivePower(object=receiver.uid, power=1)])

        caravan_choice__first_defence = facts.Option(state_from=caravan_choice.uid, state_to=first_defence.uid,
                                                     type='jump_defence', start_actions=[facts.Message(type='choose_defence'),])
        caravan_choice__move_to_attack = facts.Option(state_from=caravan_choice.uid, state_to=move_to_attack.uid,
                                                      type='jump_attack', start_actions=[facts.Message(type='choose_attack'),])

        first_defence__first_defence_continue = facts.Option(state_from=first_defence.uid, state_to=first_defence_continue.uid,
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

                 first_defence__first_defence_continue,
                 first_defence__move_to_attack,

                 first_defence_continue,

                 facts.Answer(state_from=first_defence_continue.uid, state_to=second_moving.uid, condition=True),
                 facts.Answer(state_from=first_defence_continue.uid, state_to=finish_defence_failed.uid, condition=False),

                 second_moving,

                 facts.Jump(state_from=second_moving.uid, state_to=second_defence.uid),

                 second_defence,

                 facts.Answer(state_from=second_defence.uid, state_to=finish_defence.uid, condition=True),
                 facts.Answer(state_from=second_defence.uid, state_to=finish_defence_failed.uid, condition=False),

                 finish_defence,

                 move_to_attack,

                 facts.Jump(state_from=move_to_attack.uid, state_to=attack.uid),

                 attack,

                 facts.Answer(state_from=attack.uid, state_to=run.uid, condition=True, start_actions=(facts.Message(type='start_run'),)),
                 facts.Answer(state_from=attack.uid, state_to=finish_attack_failed.uid, condition=False),

                 run,

                 facts.Jump(state_from=run.uid, state_to=fight.uid),

                 fight,

                 facts.Answer(state_from=fight.uid, state_to=hide.uid, condition=True, start_actions=(facts.Message(type='start_hide'),)),
                 facts.Answer(state_from=fight.uid, state_to=finish_attack_failed.uid, condition=False),

                 hide,

                 facts.Jump(state_from=hide.uid, state_to=finish_attack.uid),

                 finish_attack,

                 facts.OptionsLink(options=(caravan_choice__first_defence.uid, first_defence__first_defence_continue.uid)),

                 finish_defence_failed,
                 finish_attack_failed
                ]

        line.extend(participants)

        return line

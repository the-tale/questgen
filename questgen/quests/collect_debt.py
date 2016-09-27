# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import logic
from questgen import requirements
from questgen import actions
from questgen import relations


class CollectDebt(QuestBetween2):
    TYPE = 'collect_debt'
    TAGS = ('can_start', 'has_subquests') # can_continue can not be used, since quest has no FAILED finish

    @classmethod
    def find_receiver(cls, selector, initiator):
        return selector.new_person(restrict_social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.PARTNER),),
                                   social_connections=((initiator.uid, relations.SOCIAL_RELATIONS.CONCURRENT),))

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description='Начало: выбить долг',
                            require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid),
                                     requirements.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                            actions=[actions.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        choose_method = facts.Choice(uid=ns+'choose_method',
                                     description='Выбрать метод получения долга',
                                     require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                     actions=[actions.Message(type='move_to_receiver')])


        attack = facts.Question(uid=ns+'attack',
                                description='сражение с подручными должника',
                                require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                actions=[actions.Message(type='attack'),
                                         actions.Fight(mercenary=True)],
                                condition=[requirements.IsAlive(object=hero.uid)])

        finish_attack_successed = facts.Finish(uid=ns+'finish_attack_successed',
                                               start=start.uid,
                                               results={ initiator.uid: RESULTS.SUCCESSED,
                                                         receiver.uid: RESULTS.FAILED},
                                               nesting=nesting,
                                               description='долг выбит',
                                               require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                               actions=[actions.GiveReward(object=hero.uid, type='finish_attack_successed')])

        finish_attack_failed = facts.Finish(uid=ns+'finish_attack_failed',
                                            start=start.uid,
                                            results={ initiator.uid: RESULTS.NEUTRAL,
                                                      receiver.uid: RESULTS.NEUTRAL},
                                            nesting=nesting,
                                            description='не удалось выбить долг',
                                            actions=[actions.Message(type='finish_attack_failed')])

        help = facts.State(uid=ns+'help',
                           description='помочь должнику',
                           require=[requirements.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        finish_help = facts.Finish(uid=ns+'finish_help',
                                   start=start.uid,
                                   results={ initiator.uid: RESULTS.SUCCESSED,
                                             receiver.uid: RESULTS.SUCCESSED},
                                   nesting=nesting,
                                   description='помощь оказана',
                                   require=[requirements.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                   actions=[actions.GiveReward(object=hero.uid, type='finish_help')])

        help_quest = selector.create_quest_from_person(nesting=nesting+1, initiator=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in logic.filter_subquest(help_quest, nesting):
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Jump(state_from=help.uid, state_to=help_fact.uid, start_actions=[actions.Message(type='before_help')]))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.results[receiver.uid] == RESULTS.SUCCESSED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish_help.uid, start_actions=[actions.Message(type='after_successed_help')]))
                else:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=attack.uid, start_actions=[actions.Message(type='after_failed_help')]))

        subquest = facts.SubQuest(uid=ns+'help_subquest', members=logic.get_subquest_members(help_quest))

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=choose_method.uid),

                 choose_method,

                 facts.Option(state_from=choose_method.uid, state_to=attack.uid, type='attack', markers=[relations.OPTION_MARKERS.AGGRESSIVE]),
                 facts.Option(state_from=choose_method.uid, state_to=help.uid, type='help', markers=[relations.OPTION_MARKERS.UNAGGRESSIVE]),

                 help,
                 attack,

                 facts.Answer(state_from=attack.uid, state_to=finish_attack_successed.uid, condition=True, start_actions=[actions.Message(type='attack_successed')]),
                 facts.Answer(state_from=attack.uid, state_to=finish_attack_failed.uid, condition=False, start_actions=[actions.Message(type='attack_failed')]),

                 finish_attack_successed,
                 finish_attack_failed,
                 finish_help,

                 subquest
                ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line

# coding: utf-8
import itertools

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class CollectDebt(QuestBetween2):
    TYPE = 'collect_debt'
    TAGS = ('can_start', )

    # normal - normal quest
    # special - special quest
    # can_start - can be first quest in tree
    # can_continue - can be not first quest in tree

    @classmethod
    def construct(cls, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            is_entry=selector.is_first_quest,
                            description=u'Начало: выбить долг',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid),
                                     facts.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        choose_method = facts.Choice(uid=ns+'choose_method',
                                     description=u'Выбрать метод получения долга',
                                     require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])


        attack = facts.State(uid=ns+'attack',
                            description=u'сражение с подручными должника',
                            actions=[facts.Fight(uid='fight_1')])

        finish_attack = facts.Finish(uid=ns+'finish_attack',
                                     type='finish_attack',
                                     result=RESULTS.SUCCESSED,
                                     description=u'долг выбит',
                                     actions=[facts.Message(type='finish_attack'),
                                              facts.GivePower(object=initiator.uid, power=1),
                                              facts.GivePower(object=receiver.uid, power=-1)])

        help = facts.State(uid=ns+'help',
                           description=u'помочь должнику')

        finish_help = facts.Finish(uid=ns+'finish_help',
                                   type='finish_help',
                                   result=RESULTS.SUCCESSED,
                                   description=u'помощь оказана',
                                   actions=[facts.Message(type='finish_help'),
                                            facts.GivePower(object=initiator.uid, power=1),
                                            facts.GivePower(object=receiver.uid, power=1)])

        help_quest = selector._qb.create_quest_from_person(selector, initiator=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in help_quest:
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Jump(state_from=help.uid, state_to=help_fact.uid))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.result == RESULTS.SUCCESSED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish_help.uid))
                else:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=attack.uid))

        subquest = facts.SubQuest(uid=ns+'help_subquest',
                                  members = [f.uid for f in itertools.chain(help_quest, help_extra) if isinstance(f, (facts.State, facts.Jump, facts.OptionsLink))])

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=choose_method.uid),

                 choose_method,

                 facts.Option(state_from=choose_method.uid, state_to=attack.uid, type='attack'),
                 facts.Option(state_from=choose_method.uid, state_to=help.uid, type='help'),

                 help,
                 attack,

                 facts.Jump(state_from=attack.uid, state_to=finish_attack.uid),

                 finish_attack,
                 finish_help,

                 subquest
                ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line

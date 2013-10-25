# coding: utf-8

from questgen.knowledge_base import KnowledgeBase # «база знаний» о мире и задании
from questgen import facts # все факты
from questgen.selectors import Selector # вспомогательный класс для поиска нужных фактов
from questgen import restrictions # ограничения, которые обязательно должны выплнятся в валидном задании
from questgen import transformators # трансформации, которые можно делать над базой знаний
from questgen import machine # механизм для итерации по заданию

# импортируем квесты
from questgen.quests.quests_base import QuestsBase
from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.quests.delivery import Delivery
from questgen.quests.caravan import Caravan
from questgen.quests.collect_debt import CollectDebt
from questgen.quests.help_friend import HelpFriend
from questgen.quests.interfere_enemy import InterfereEnemy
from questgen.quests.help import Help

from questgen.relations import PROFESSION

# список ограничений для фактов о мире
WORLD_RESTRICTIONS = [restrictions.SingleLocationForObject(),
                      restrictions.ReferencesIntegrity()]

# список ограничений для графа задания
QUEST_RESTRICTIONS =  [restrictions.SingleStartStateWithNoEnters(), # только одна начальная вершина для задания
                       restrictions.FinishStateExists(), # существуют завершающие вершины
                       restrictions.AllStatesHasJumps(), # существуют переходы из всех состояний
                       restrictions.ConnectedStateJumpGraph(), # граф связаный
                       restrictions.NoCirclesInStateJumpGraph(), # граф без циклов
                       restrictions.MultipleJumpsFromNormalState(), # каждая обычная вершина имеет только одну исходящую дугу
                       restrictions.ChoicesConsistency(), # проверяем целостность развилок
                       restrictions.QuestionsConsistency(), # проверяем целостность условных узлов
                       restrictions.FinishResultsConsistency() # проверяем, что для каждого окончания квеста указаны результаты для каждого его участника
                       ]


# создаём задание
# эта функция может вызвать исключение questgen.exceptions.RollBackError и это её нормальное поведение
# исключение означает, что создать задание не получилось и надо повторить попытку
def create_quest():

    # формируем список заданий для генерации
    qb = QuestsBase()
    qb += [Spying, Hunt, Hometown, SearchSmith, Delivery, Caravan, CollectDebt, HelpFriend, InterfereEnemy, Help]

    kb = KnowledgeBase()

    # описываем мир
    kb += [ facts.Hero(uid='hero'), # наш герой

            facts.Place(uid='place_1', terrains=(1,)), # есть место с идентификатором place_1 и типами ландшафта 1,
            facts.Place(uid='place_2', terrains=(0,)),
            facts.Place(uid='place_3', terrains=(0,)),
            facts.Place(uid='place_4', terrains=(1,)),
            facts.Place(uid='place_5', terrains=(2,)),
            facts.Place(uid='place_6', terrains=(1,)),
            facts.Place(uid='place_7', terrains=(2,)),
            facts.Place(uid='place_8', terrains=(2,)),
            facts.Place(uid='place_9', terrains=(1,)),
            facts.Place(uid='place_10', terrains=(2,)),

            facts.Person(uid='person_1', profession=PROFESSION.NONE), # есть персонаж с идентификатором perons_1 и без профессии
            facts.Person(uid='person_2', profession=PROFESSION.BLACKSMITH),
            facts.Person(uid='person_3', profession=PROFESSION.NONE),
            facts.Person(uid='person_4', profession=PROFESSION.NONE),
            facts.Person(uid='person_5', profession=PROFESSION.NONE),
            facts.Person(uid='person_6', profession=PROFESSION.NONE),
            facts.Person(uid='person_7', profession=PROFESSION.NONE),
            facts.Person(uid='person_8', profession=PROFESSION.NONE),
            facts.Person(uid='person_9', profession=PROFESSION.NONE),
            facts.Person(uid='person_10', profession=PROFESSION.NONE),

            facts.LocatedIn(object='person_1', place='place_1'), # персонаж person_1 находится в place_1
            facts.LocatedIn(object='person_2', place='place_2'),
            facts.LocatedIn(object='person_3', place='place_3'),
            facts.LocatedIn(object='person_4', place='place_4'),
            facts.LocatedIn(object='person_5', place='place_5'),
            facts.LocatedIn(object='person_6', place='place_6'),
            facts.LocatedIn(object='person_7', place='place_7'),
            facts.LocatedIn(object='person_8', place='place_8'),
            facts.LocatedIn(object='person_9', place='place_9'),
            facts.LocatedIn(object='person_10', place='place_10'),

            facts.LocatedIn(object='hero', place='place_1'), # герой находится в place_1

            facts.Mob(uid='mob_1', terrains=(0,)), # есть монстр, обитающий на территориях с идентификатором 0 (для задания на охоту)
            facts.PreferenceMob(object='hero', mob='mob_1'), # герой любит охотиться на монстра mob_1
            facts.PreferenceHometown(object='hero', place='place_2'), # герой считате родным место place_2
            facts.PreferenceFriend(object='hero', person='person_4'), # герой дружит с person_4
            facts.PreferenceEnemy(object='hero', person='person_5'), # герой враждует с person_5

            # указываем, что обновление экипировки стоит 777 монет (для задания SearchSmith)
            # facts.HasMoney(object='hero', money=888), # если этот факт раскоментировать то в этом задании герой купит экипировку, а не пойдёт делать задание кузнеца
            facts.UpgradeEquipmentCost(money=777),

            facts.OnlyGoodBranches(object='place_2'), # не вредить месту place_2
            facts.OnlyGoodBranches(object='person_4'), # не вредить персонажу person_4
            facts.OnlyBadBranches(object='person_5') ] # не помогать персонажу person_5


    kb.validate_consistency(WORLD_RESTRICTIONS) # проверяем ограничения на мир,

    selector = Selector(kb, qb)

    # создаём квест (получаем список фактов)
    quests_facts = selector.create_quest_from_place(nesting=0,
                                                    initiator_position=kb['place_1'],
                                                    tags=('can_start', ))

    kb += quests_facts

    transformators.activate_events(kb) # активируем события (из нескольких вершин графа оставляем одну, остальные удаляем)
    transformators.remove_restricted_states(kb) # удаляем состояния, в которые нельзя переходить (например, которые вредят тому, кому вредить нельщя)
    transformators.remove_broken_states(kb) # чистим граф задания от разрушений, вызванных предыдущими действиями
    transformators.determine_default_choices(kb) # определяем выборы по умолчанию на развилках

    kb.validate_consistency(WORLD_RESTRICTIONS) # ещё раз проверяем мир
    kb.validate_consistency(QUEST_RESTRICTIONS) # проверяем граф задания (вдруг полностью разрушен)

    return kb


# интерпретатор задания
class Interpretator(object):

    def __init__(self, kb):
        self.kb = kb
        # создаём механизм для итерации по графу и передаём в него коллбэки
        self.machine = machine.Machine(knowledge_base=kb,
                                       on_state=self._on_state,
                                       on_jump_start=self._on_jump_start,
                                       on_jump_end=self._on_jump_end)

    # когда входим в новую вершину
    def _on_state(self, state):
        print 'on state: %s' % state.uid

        if isinstance(state, facts.Start):
            print '    starting quest "%s"' % state.type

        if isinstance(state, facts.Finish):
            print '    finishing quest with result "%s"' % state.result

        print '    find %d actions' % len(state.actions)
        for action in state.actions:
            print '    do %r' % action

    # когда переходим на новую дугу
    def _on_jump_start(self, jump):
        print 'on jump start: %s' % jump.uid
        print '    find %d actions' % len(jump.start_actions)
        for action in jump.start_actions:
            print '    do %r' % action

    # когда уходим из дуги
    def _on_jump_end(self, jump):
        print 'on jump end: %s' % jump.uid
        print '    find %d actions' % len(jump.end_actions)
        for action in jump.end_actions:
            print '    do %r' % action

    # делаем квест
    def process(self):
        while self.do_step():
            print '---- next step ----'

    # один шаг квеста
    def do_step(self):
        # синхронизируем базу с реальным состоянием вещей
        # например, указываем новое положение героя
        self.sync_knowledge_base()

        # можем ли перейти дальше
        if self.machine.can_do_step():
            self.machine.step() # переходим
            return True

        if self.machine.is_processed: # прошли по всему заданию
            return False

        # если не можем сделать шаг, значит есть какие-то требования, которые надо удовлетворить
        # например, переместить героя
        if self.machine.next_state:
            self.satisfy_requirements(self.machine.next_state)

        return True

    def sync_knowledge_base(self):
        print 'sync knowlege base with real situation'

    def satisfy_requirements(self, state):
        for requirement in state.require:
            if not requirement.check(self.kb):
                if isinstance(requirement, (facts.LocatedIn, facts.LocatedNear)):
                    self._satisfy_position(requirement)

    def _satisfy_position(self, requirement):
        self.kb -= [location
                    for location in self.kb.filter(facts.LocatedIn)
                    if location.object == requirement.object]

        self.kb -= [location
                    for location in self.kb.filter(facts.LocatedNear)
                    if location.object == requirement.object]

        new_position = requirement.__class__(object=requirement.object, place=requirement.place)
        self.kb += new_position

        print 'change position: %r' % new_position




if __name__ == '__main__':
    kb = create_quest()
    interpretator = Interpretator(kb=kb)
    interpretator.process()

# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen.graph_drawer import Drawer
from questgen.selectors import Selector
from questgen import restrictions

from questgen.quests.quests_base import QuestsBase
from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.quests.delivery import Delivery
from questgen.quests.caravan import Caravan
from questgen.quests.collect_debt import CollectDebt
from questgen.quests.simple import Simple

from questgen.relations import PROFESSION

QUESTS = [Spying, Hunt, Hometown, SearchSmith, Delivery, Caravan, CollectDebt, Simple]

qb = QuestsBase()
qb += [Simple]

for Quest in QUESTS:

    print 'process quest: %s' % Quest.TYPE

    kb = KnowledgeBase()

    kb += [ facts.Hero(uid='hero'),

            facts.Place(uid='place_1', terrains=(1,)),
            facts.Place(uid='place_2', terrains=(0,)),
            facts.Place(uid='place_3', terrains=(0,)),
            facts.Place(uid='place_4', terrains=(1,)),
            facts.Place(uid='place_5', terrains=(2,)),

            facts.Person(uid='person_1', profession=PROFESSION.NONE),
            facts.Person(uid='person_2', profession=PROFESSION.BLACKSMITH),
            facts.Person(uid='person_3', profession=PROFESSION.NONE),
            facts.Person(uid='person_4', profession=PROFESSION.NONE),
            facts.Person(uid='person_5', profession=PROFESSION.NONE),

            facts.LocatedIn(object='person_1', place='place_1'),
            facts.LocatedIn(object='person_2', place='place_2'),
            facts.LocatedIn(object='person_3', place='place_3'),
            facts.LocatedIn(object='person_4', place='place_4'),
            facts.LocatedIn(object='person_5', place='place_5'),

            facts.LocatedIn(object='hero', place='place_1'),

            facts.Mob(uid='mob_1', terrains=(0,)),
            facts.PreferenceMob(object='hero', mob='mob_1'),
            facts.PreferenceHometown(object='hero', place='place_2') ]

    selector = Selector(kb, qb)
    kb += Quest.construct_from_place(selector, selector.new_place(candidates=('place_1',)))

    kb.validate_consistency([restrictions.SingleStartStateWithNoEnters(),
                             restrictions.FinishStateExists(),
                             restrictions.AllStatesHasJumps(),
                             restrictions.SingleLocationForObject(),
                             restrictions.ReferencesIntegrity(),
                             restrictions.ConnectedStateJumpGraph(),
                             restrictions.NoCirclesInStateJumpGraph(),
                             # restrictions.MultipleJumpsFromNormalState(),
                             restrictions.ChoicesConsistency()])

    drawer = Drawer(knowledge_base=kb)
    drawer.draw('./svgs/%s.svg' % Quest.TYPE)

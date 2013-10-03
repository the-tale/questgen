# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen.graph_drawer import Drawer
from questgen.selectors import Selector
from questgen import restrictions

from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.relations import PROFESSION

QUESTS = [Spying, Hunt, Hometown, SearchSmith]

for Quest in QUESTS:

    print 'process quest: %s' % Quest.TYPE

    kb = KnowledgeBase()

    kb += [ facts.Hero(uid='hero'),

            facts.Place(uid='place_1', terrains=(1,)),
            facts.Place(uid='place_2', terrains=(0,)),
            facts.Place(uid='place_3', terrains=(0,)),

            facts.Person(uid='person_1', profession=PROFESSION.NONE),
            facts.Person(uid='person_2', profession=PROFESSION.BLACKSMITH),
            facts.Person(uid='person_3', profession=PROFESSION.NONE),

            facts.LocatedIn(object='person_1', place='place_1'),
            facts.LocatedIn(object='person_2', place='place_2'),
            facts.LocatedIn(object='person_3', place='place_3'),

            facts.Mob(uid='mob_1', terrains=(0,)),
            facts.PreferenceMob(object='hero', mob='mob_1'),
            facts.PreferenceHometown(object='hero', place='place_2') ]

    kb += Quest.construct_from_nothing(kb, Selector(kb))


    kb.validate_consistency([restrictions.SingleStartState(),
                             restrictions.FinishStateExists(),
                             restrictions.NoJumpsFromFinish(),
                             restrictions.SingleLocationForObject(),
                             restrictions.ReferencesIntegrity(),
                             restrictions.ConnectedStateJumpGraph(),
                             restrictions.NoCirclesInStateJumpGraph(),
                             # restrictions.MultipleJumpsFromNormalState(),
                             restrictions.ChoicesConsistency()])

    drawer = Drawer(knowledge_base=kb)
    drawer.draw('./svgs/%s.svg' % Quest.TYPE)

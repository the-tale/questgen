# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import ( Start,
                             State,
                             Jump,
                             Finish,
                             Event,
                             Place,
                             Person,
                             LocatedIn,
                             Choice,
                             Option)
from questgen.graph_drawer import Drawer
from questgen.restrictions import (SingleStartState,
                                   NoJumpsFromFinish,
                                   SingleLocationForObject,
                                   ReferencesIntegrity,
                                   ConnectedStateJumpGraph,
                                   NoCirclesInStateJumpGraph)

kb = KnowledgeBase()

kb += [SingleStartState(),
       NoJumpsFromFinish(),
       SingleLocationForObject(),
       ReferencesIntegrity(),
       ConnectedStateJumpGraph(),
       NoCirclesInStateJumpGraph()]

# Todo: person_target обнрауживает слежку
#       просьбы meta: ничем не занимается,
#                     соврать,
#                     соврать, а результаты слежки доложить meta
#       просьбы мета давать где-то на середине пути
#       возвращать героя к каждому из заказчиков

# spying
kb += [ Place(uid='place_customer'),
        Place(uid='place_target'),

        Person(uid='customer'),
        Person(uid='target'),

        Start(label=u'Начало',
              description=u'Задание на шпионаж',
              require=[LocatedIn('hero', 'place_customer'),
                       LocatedIn('customer', 'place_customer'),
                       LocatedIn('target', 'place_target')]),

        Jump(state_from=Start.UID, state_to='rt_nh'),
        Choice(uid='rt_nh', label=u'Дорога к цели', description=u'Ничего не происходит', require=[LocatedIn('hero', 'place_target')]),
        Option(state_from='rt_nh', state_to='ht_spying'),
        Option(state_from='rt_nh', state_to='ht_open_up'),

        State(uid='ht_spying', label=u'Шпионаж', description=u'Герой шпионит за целью'),
        State(uid='ht_open_up', label=u'Раскрыться', description=u'Сообщить цели о шпионаже'),

        Jump(state_from='ht_spying', state_to='hc_spying'),
        Finish(uid='hc_spying', label=u'Шпионить', description=u'Шпионить до конца и вернуться обратно', require=[LocatedIn('hero', 'place_customer')]),

        Finish(uid='open_up_finish',
               label=u'Завершить задаие',
               description=u'Завершить задание и остатсья в городе цели',
               tags=('open_up_variants',),
               require=[LocatedIn('hero', 'place_target')]),
        Finish(uid='open_up_lying',
               label=u'Обмануть заказчика',
               description=u'Вернуться к заказчику и сообщить ложную информацию',
               tags=('open_up_variants',),
               require=[LocatedIn('hero', 'place_customer')]),

        Jump(state_from='ht_open_up', state_to='open_up_finish'),
        Jump(state_from='ht_open_up', state_to='open_up_lying'),
]

kb.validate_consistency()

drawer = Drawer(knowledge_base=kb)
drawer.draw('./test_draw.svg')

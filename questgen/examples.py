# coding: utf-8

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Hero, Place, Person, Start, Finish, Choice, Jump, LocatedIn
from questgen.states import Option

kb = KnowledgeBase()

kb += [
    Hero(uid='hero'),
    Place(uid='place_from', label='место отправления'),
    Person(uid='person_from', label='отправитель'),
    Place(uid='place_to', label='место назначения'),
    Place(uid='place_steal', label='место схрона'),
    Person(uid='person_to', label='получатель'),

    Start(uid='st_start', require=(LocatedIn('person_from', 'place_from'),
                                   LocatedIn('person_to', 'place_to'),
                                   LocatedIn('hero', 'place_from'))),

    Choice(uid='st_steal'),
    Option(uid='st_steal.steal', choice='st_steal', label='украсть'),
    Option(uid='st_steal.deliver', choice='st_steal', label='доставить'),

    Finish(uid='st_finish_delivered', require=(LocatedIn('hero', 'place_to'),)),
    Finish(uid='st_finish_stealed', require=(LocatedIn('hero', 'place_steal'),)),

    Jump('st_start', 'st_steal'),
    Jump('st_steal.deliver', 'st_finish_delivered'),
    Jump('st_steal.steal', 'st_finish_stealed'),
    ]

# Quest('delivery_quest', globals())

# База знаний делится на уровни
# верхни уровень - константные данные о мире общие для всех игроков
# средний уровень - данные, специфичные для заданий этого типа
# нижний уровень - данные, специфичные для конкретно этого задания
# при поиске, информация сначала ищется на нижнем уровне, потом на верхнем
#
# Выбор не является сюжетной точкой, вместо этого он привязывается к каждому переходу
# Состояние же (точка сюжета) устанавливает цели героя (куда придти, что сделать),
# которые он должен достигнуть, чтобы перейти в него
# при изменении выбора, меняется переход (следовательно конечное состояние) и цели героя
#
# то же самое и с событиями, при возникновении они меняют переход
#
# при создании задания, для каждого события (и выбора) сразу решается случается оно или нет,
# иными словами они становятся константсными данными,
# часть которых (а именно автоматические выборы) может измениться в пользу выбора игрока
#
# События могут быть альтернативными, в этом случае может случиться только одно событие из группы
# но оно случается обязательно, для варианта "ничего не случилось" можно ввести фейковое событие
#
# Нужны ли вообще переходы?
# Условия для автоматического выбора героем (на основе характера)
# Влияние выбора на характер (плохой-хороший, честный-лжец)
#

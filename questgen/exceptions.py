# coding: utf-8


class QuestgenError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(QuestgenError, self).__init__(self.MSG % kwargs)

####################################################################
# knowledge base
####################################################################p

class KnowledgeBaseError(QuestgenError): pass

class DuplicatedFactError(KnowledgeBaseError):
    MSG = 'can not add fact %(fact)r to knowlege base - it already in base'

class WrongFactTypeError(KnowledgeBaseError):
    MSG = 'can not add fact %(fact)r to knowlege base - wrong type'

class NoFactError(KnowledgeBaseError):
    MSG = '%(fact)s not in knowledge base'

####################################################################
# facts
####################################################################
class FactsError(QuestgenError): pass

class WrongChangeAttributeError(KnowledgeBaseError):
    MSG = 'can not change fact %(fact)r - unknown attribute "%(attribute)s"'

class UIDDidNotSetupped(FactsError):
    MSG = 'uid for "%(fact)r did not setupped'

####################################################################
# records
####################################################################
class RecordsError(QuestgenError): pass

class RequiredRecordAttributeError(KnowledgeBaseError):
    MSG = 'can not create record %(record)r - attribute "%(attribute)s" not specified'

class WrongRecordAttributeError(KnowledgeBaseError):
    MSG = 'can not create record %(record)r - wrong attribute "%(attribute)s"'

####################################################################
# machine
####################################################################
class MachineError(QuestgenError): pass

class NoJumpsAvailableError(MachineError):
    MSG = 'no jumps available for state %(state)r'

class NoJumpsFromLastStateError(MachineError):
    MSG = 'no jumps available for last state %(state)r'

class MoreThenOneJumpsAvailableError(MachineError):
    MSG = 'more then oneo jumps available for state %(state)r'


####################################################################
# transformators
####################################################################
class TransformatorsError(QuestgenError): pass

class NoEventMembersError(TransformatorsError):
    MSG = 'no tagged event members for event "%(event)r"'

class OptionWithTwoLinksError(TransformatorsError):
    MSG = 'option "%(option)r" has more then one link'

class LinkedOptionWithProcessedChoiceError(TransformatorsError):
    MSG = 'choice of option "%(option)r" has already had default option. Probably you have mess with linked options'


####################################################################
# quests
####################################################################

class QuestsBaseError(QuestgenError): pass

class DuplicatedQuestError(QuestsBaseError):
    MSG = 'can not add quest %(quest)r to quests base - it already in base'

class WrongQuestTypeError(QuestsBaseError):
    MSG = 'can not add quest %(quest)r to quests base - wrong type'


####################################################################
# roll back errors
####################################################################

class RollBackError(QuestgenError):
    MSG = 'something is wrong (%(message)), do rollback'

class NoQuestChoicesRollBackError(RollBackError):
    MSG = 'no quests choices for next quest'


####################################################################
# selectoes
####################################################################

class SelectorsBaseError(RollBackError): pass

class NoFactSelectedError(SelectorsBaseError):
    MSG = 'can not found fact with method "%(method)s" and arguments: %(arguments)s — with reserve: %(reserved)s'


####################################################################
# graph drawer
####################################################################p

class GraphDrawerError(QuestgenError): pass


class CanNotCreateLabelForFactError(GraphDrawerError):
    MSG = 'can not create label for fact: %(fact)s'


class CanNotCreateLabelForRequirementError(GraphDrawerError):
    MSG = 'can not create label for requirement: %(requirement)s'


class CanNotCreateLabelForActionError(GraphDrawerError):
    MSG = 'can not create label for action: %(action)s'

# coding: utf-8


class QuestgenError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(QuestgenError, self).__init__(self.MSG % kwargs)

####################################################################
# knowledge base
####################################################################

class KnowledgeBaseError(QuestgenError): pass

class DuplicatedFactError(KnowledgeBaseError):
    MSG = u'can not add fact %(fact)r to knowlege base - it already in base'

class WrongFactTypeError(KnowledgeBaseError):
    MSG = u'can not add fact %(fact)r to knowlege base - wrong type'

class NoFactError(KnowledgeBaseError):
    MSG = u'%(fact)s not in knowledge base'

####################################################################
# facts
####################################################################
class FactsError(QuestgenError): pass

class WrongChangeAttributeError(KnowledgeBaseError):
    MSG = u'can not change fact %(fact)r - unknown attribute "%(attribute)s"'

# class OptionUIDWithoutChoicePart(FactsError):
#     MSG = u'Option uid "%(option)r" MUST starts with parent choice uid followed by dot'

class UIDDidNotSetupped(FactsError):
    MSG = u'uid for "%(fact)r did not setupped'

####################################################################
# machine
####################################################################
class MachineError(QuestgenError): pass

class NoJumpsAvailableError(KnowledgeBaseError):
    MSG = u'no jumps available for state %(state)r'


####################################################################
# transformators
####################################################################
class TransformatorsError(QuestgenError): pass

class NotJumpFactInEventGroupError(TransformatorsError):
    MSG = u'event group (%(event)s) MUST contain only jump facts, not "%(fact)r" fact'

class NoTaggedEventMembersError(TransformatorsError):
    MSG = u'no tagged event members for event "%(event)r"'

class MoreThenOneEventTagError(TransformatorsError):
    MSG = u'fact "%(fact)r" marked more then one event tags'

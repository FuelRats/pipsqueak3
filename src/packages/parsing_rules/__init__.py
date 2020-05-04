import pyparsing
from uuid import UUID

"""
Matches a valid IRC nickname. 
Token MUST start with a letter but MAY contain numerics and some special chars
"""
irc_name = pyparsing.Word(initChars=pyparsing.alphas, bodyChars=pyparsing.alphanums + "[]{}|:-_<>")

""" matches a well formed UUID4"""
api_id = pyparsing.Word(initChars='@', bodyChars=pyparsing.hexnums + '-', min=36, max=37)
num_word = pyparsing.Word(pyparsing.nums)
"""Matches a case number"""
case_number = (
    # may lead with 'case'
        api_id.setParseAction(lambda token: UUID(token[0][1:]))
        | pyparsing.Optional(pyparsing.Literal('#').suppress())
        + pyparsing.Word(pyparsing.nums).setParseAction(lambda token: int(token[0]))

)

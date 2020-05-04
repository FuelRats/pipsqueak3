import pyparsing
from uuid import UUID

"""
Matches a valid IRC nickname. 
Token MUST start with a letter but MAY contain numerics and some special chars
"""
irc_name = pyparsing.Word(initChars=pyparsing.alphas, bodyChars=pyparsing.alphanums + "[]{}|:-_<>")

""" matches a well formed UUID4"""
api_id = pyparsing.Word(pyparsing.hexnums + '-', min=36, max=36)
num_word = pyparsing.Word(pyparsing.nums) & pyparsing.WordEnd()
"""Matches a case number"""
case_number = (
    # may lead with 'case'
        pyparsing.Optional(pyparsing.CaselessLiteral("case").suppress())
        # case numbers may be prefixed with either `c` or `#` e.g. `#3`
        + pyparsing.Optional(pyparsing.oneOf("c # @").suppress())
        # case numbers are numerical, and are the subject token.
        + api_id.setParseAction(lambda token: UUID(token[0]))
        | pyparsing.Word(pyparsing.nums).setParseAction(lambda token: int(token[0]))

)

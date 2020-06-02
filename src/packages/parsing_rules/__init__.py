from uuid import UUID

import pyparsing

"""
Matches a valid IRC nickname. 
Token MUST start with a letter but MAY contain numerics and some special chars
"""
irc_name = pyparsing.Word(initChars=pyparsing.alphas, bodyChars=pyparsing.alphanums + "[]{}|:-_<>\\/")

""" matches a well formed UUID4"""
api_id = pyparsing.Word(initChars='@', bodyChars=pyparsing.hexnums + '-', min=36, max=37)

"""Matches a case number"""
case_number = (
    # may lead with 'case'
        api_id.setParseAction(lambda token: UUID(token[0][1:]))
        | pyparsing.Optional(pyparsing.Literal('#').suppress())
        + pyparsing.Word(pyparsing.nums).setParseAction(lambda token: int(token[0]))

)

"""Matches any valid rescue identifier, converting matches to their corresponding types. """
rescue_identifier = irc_name | case_number

""" Suppresses the first word in the string. """
suppress_first_word = pyparsing.Word(pyparsing.printables).suppress()

""" matches something that looks like a timer. `d:d` """
timer = pyparsing.Word(pyparsing.nums) + ':' + pyparsing.Word(pyparsing.nums) + pyparsing.WordEnd()

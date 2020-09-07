from uuid import UUID

import pyparsing

irc_name = pyparsing.Word(initChars=pyparsing.alphas, bodyChars=pyparsing.alphanums + "[]{}|:-_<>\\/")
"""
Matches a valid IRC nickname.
 Token MUST start with a letter but MAY contain numerics and some special chars
"""

api_id = pyparsing.Word(initChars="@", bodyChars=pyparsing.hexnums + "-", min=36, max=37)
""" matches a well formed UUID4"""

case_number = (
    # may lead with 'case'
    api_id.setParseAction(lambda token: UUID(token[0][1:]))
    | pyparsing.Optional(pyparsing.Literal("#").suppress())
    + pyparsing.Word(pyparsing.nums).setParseAction(lambda token: int(token[0]))
)
"""Matches a case number"""

rescue_identifier = irc_name | case_number
"""Matches any valid rescue identifier, converting matches to their corresponding types. """

suppress_first_word = pyparsing.Word(pyparsing.printables).suppress()
""" Suppresses the first word in the string. """

timer = pyparsing.Word(pyparsing.nums) + ":" + pyparsing.Word(pyparsing.nums) + pyparsing.WordEnd()
""" matches something that looks like a timer. `d:d` """

platform = (
    pyparsing.CaselessKeyword("pc").setResultsName("pc")
    | (
        pyparsing.CaselessKeyword("ps")
        ^ pyparsing.CaselessKeyword("ps")
        ^ pyparsing.CaselessKeyword("ps4")
        ^ pyparsing.CaselessKeyword("playstation")
        ^ pyparsing.CaselessKeyword("playstation4")
        ^ pyparsing.CaselessKeyword("playstation 4")
    ).setResultsName("playstation")
    | (
        pyparsing.CaselessLiteral("xb")
        ^ pyparsing.CaselessLiteral("xb1")
        ^ pyparsing.CaselessLiteral("xbox")
        ^ pyparsing.CaselessLiteral("xboxone")
        ^ "pyparsing.CaselessLiteral(xbox one)"
    ).setResultsName("xbox")
)
"""
Matches a platform specifier
"""

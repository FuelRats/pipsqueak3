import pyparsing

"""
Matches a valid IRC nickname. 
Token MUST start with a letter but MAY contain numerics and some special chars
"""
irc_name = pyparsing.Word(initChars=pyparsing.alphas, bodyChars=pyparsing.alphanums + '[]{}|:-_<>')
case_number = (
    # may lead with 'case'
        pyparsing.Optional(pyparsing.Suppress(pyparsing.CaselessLiteral("case")))
        # case numbers may be prefixed with either `c` or `#` e.g. `#3`
        + pyparsing.Optional(pyparsing.Suppress(pyparsing.oneOf("c #")))
        # case numbers are numerical, and are the subject token.
        + pyparsing.Word(pyparsing.nums)
)

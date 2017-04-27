# -*- coding: utf-8 -*-
"""
    pygments.lexers.solidity
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexer for the Solidity language.

    :copyright: Copyright 2006-2015 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, default, using, \
    this, words, combined
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Other

__all__ = ['SolidityLexer']


class SolidityLexer(RegexLexer):
    """
    For Solidity source code.
    """

    name = 'Solidity'
    aliases = ['sol', 'solidity']
    filenames = ['*.sol']
    mimetypes = []

    flags = re.DOTALL | re.UNICODE | re.MULTILINE

    def type_names(prefix, sizerange):
        """
        Helper for type name generation, like: bytes1 .. bytes32
        """
        namelist = []
        for i in sizerange: namelist.append(prefix + str(i))
        return tuple(namelist)

    def type_names_mn(prefix, sizerangem, sizerangen):
        """
        Helper for type name generation, like: fixed0x8 .. fixed0x256
        """
        lm = []
        ln = []
        namelist = []

        # construct lists out of ranges
        for i in sizerangem: lm.append(i)
        for i in sizerangen: ln.append(i)

        # sizes (in bits) are valid if (%8 == 0) and (m+n <= 256)
        # first condition is covered by passing proper sizerange{m,n}
        validpairs = [tuple([m,n]) for m in lm for n in ln if m+n<=256]
        for i in validpairs:
            namelist.append(prefix + str(i[0]) + 'x' + str(i[1]))

        return tuple(namelist)


    tokens = {
        'assembly': [
            include('comments'),
            include('numbers'),
            include('strings'),
            include('whitespace'),

            (r'\{', Punctuation, '#push'),
            (r'\}', Punctuation, '#pop'),
            (r'[(),]', Punctuation),
            (r':=|=:', Operator),
            (r'(let)(\s*)(\w*\b)', bygroups(Operator.Word, Text, Name.Variable)),
            (r'(\w*\b)(\:[^=])', bygroups(Name.Label, Punctuation)),

            (r'(stop|add|mul|sub|div|sdiv|mod|smod|addmod|mulmod|exp|'
             r'signextend|lt|gt|slt|sgt|eq|iszero|and|or|xor|not|byte|'
             r'sha3|address|balance|origin|caller|callvalue|calldataload|'
             r'calldatasize|calldatacopy|codesize|codecopy|gasprice|'
             r'extcodesize|extcodecopy|blockhash|coinbase|timestamp|'
             r'number|difficulty|gaslimit|pop|mload|mstore|mstore8|sload|'
             r'sstore|jump|jumpi|pc|msize|gas|jumpdest|push1|push2|'
             r'push32|dup1|dup2|dup16|swap1|swap2|swap16|log0|log1|log4|'
             r'create|call|callcode|return|delegatecall|suicide)\b',
             Name.Function),

            # everything else is either a local/external var, or label
            ('[a-zA-Z_]\w*', Name)
        ],
        'comments': [
            (r'//([\w\W]*?\n)', Comment.Single),
            (r'/[*][\w\W]*?[*]/', Comment.Multiline),
            # Open until EOF, so no ending delimiter
            (r'/[*][\w\W]*', Comment.Multiline),
        ],
        'keywords-other': [
            (words(('for', 'in', 'while', 'do', 'break', 'return',
                    'returns', 'continue', 'if', 'else', 'throw',
                    'new', 'delete'),
                   suffix=r'\b'), Keyword),

            (r'assembly\b', Keyword, 'assembly'),

            (words(('contract', 'enum', 'event', 'function',
                    'library', 'mapping', 'modifier', 'struct', 'var'),
                   suffix=r'\b'), Keyword.Declaration),

            (r'(import|using)\b', Keyword.Namespace),

            # misc keywords
            (r'pragma solidity\b', Keyword.Reserved),
            (r'(_|as|constant|default|from|is)\b', Keyword.Reserved),
            # built-in modifier
            (r'payable\b', Keyword.Reserved),
            # variable location specifiers
            (r'(memory|storage)\b', Keyword.Reserved),
            # method visibility specifiers
            (r'(external|internal|private|public)\b', Keyword.Reserved),
            # event parameter specifiers
            (r'(anonymous|indexed)\b', Keyword.Reserved),
            # added in `solc v0.4.0`, not covered elsewhere
            (r'(abstract|interface|pure|static|view)\b', Keyword.Reserved),

            (r'(true|false)\b', Keyword.Constant),
            (r'(wei|finney|szabo|ether)\b', Keyword.Constant),
            (r'(seconds|minutes|hours|days|weeks|years)\b', Keyword.Constant),
        ],
        'keywords-types': [
            (words(('address', 'bool', 'byte', 'bytes', 'int', 'fixed',
                    'string', 'ufixed', 'uint'),
                   suffix=r'\b'), Keyword.Type),

            (words(type_names('int', range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names('uint', range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names('bytes', range(1, 32+1)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names_mn('fixed', range(0, 256+1, 8), range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names_mn('ufixed', range(0, 256+1, 8), range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),
        ],
        'numbers': [
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            (r'[0-9]+', Number.Integer),
        ],
        'string-parse-common': [
            # escapes
            (r'\\(u[0-9a-fA-F]{4}|x..|[^x])', String.Escape),
            # almost everything else is plain characters
            (r'[^\\"\'\n]+', String),
            # line continuation
            (r'\\\n', String),
            # stray backslash
            (r'\\', String)
        ],
        'string-parse-double': [
            (r'"', String, '#pop'),
            (r"'", String)
        ],
        'string-parse-single': [
            (r"'", String, '#pop'),
            (r'"', String)
        ],
        'strings': [
            # hexadecimal string literals
            (r"hex'[0-9a-fA-F]+'", String),
            (r'hex"[0-9a-fA-F]+"', String),
            # usual strings
            (r'"', String, combined('string-parse-common',
                                    'string-parse-double')),
            (r"'", String, combined('string-parse-common',
                                    'string-parse-single'))
        ],
        'whitespace': [
            (r'\s+', Text)
        ],
        'root': [
            include('comments'),
            include('keywords-types'),
            include('keywords-other'),
            include('numbers'),
            include('strings'),
            include('whitespace'),

            (r'\+\+|--|\*\*|\?|:|~|&&|\|\||=>|==?|!=?|'
             r'(<<|>>>?|[-<>+*%&|^/])=?', Operator),

            (r'[{(\[;,]', Punctuation),
            (r'[})\].]', Punctuation),

            (r'(block|msg|now|this|super|tx)\b', Name.Builtin),
            # built-in members, should these be Name.Function?..
            (r'(selfdestruct|suicide)\b', Name.Builtin),
            (r'(balance|send)\b', Name.Builtin),
            (r'(call|callcode|delegatecall)\b', Name.Builtin),

            (r'(addmod|ecrecover|mulmod|ripemd160|sha256|sha3)\b', Name.Function),

            # everything else is a var/function name
            ('[a-zA-Z_]\w*', Name)
        ] # 'root'
    } # tokens
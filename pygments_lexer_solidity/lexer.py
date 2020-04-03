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
    filenames = ['*.sol', '*.solidity']
    mimetypes = ['text/x-solidity']

    flags = re.DOTALL | re.UNICODE | re.MULTILINE

    def type_names(prefix, sizerange):
        """
        Helper for type name generation, like: bytes1 .. bytes32

        Assumes that the size range passed in is valid.
        """
        namelist = []
        for i in sizerange: namelist.append(prefix + str(i))
        return tuple(namelist)

    def type_names_mn(prefix, sizerangem, sizerangen):
        """
        Helper for type name generation, like: fixed0x8 .. fixed0x256

        Assumes that the size range passed in is valid.
        """
        lm = []
        ln = []
        namelist = []

        # construct lists out of ranges
        for i in sizerangem: lm.append(i)
        for i in sizerangen: ln.append(i)

        validpairs = [tuple([m,n]) for m in lm for n in ln]
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
            (r'(let)(\s*)(\w*\b)',
             bygroups(Operator.Word, Text, Name.Variable)),
            (r'(\w*\b)(\:[^=])',
             bygroups(Name.Label, Punctuation)),

            (r'if\b', Keyword.Reserved),

            # evm instructions
            (r'(stop|add|mul|sub|div|sdiv|mod|smod|addmod|mulmod|exp|'
             r'signextend|lt|gt|slt|sgt|eq|iszero|and|or|xor|not|byte|'
             r'keccak256|sha3|address|balance|origin|caller|'
             r'callvalue|calldataload|calldatasize|calldatacopy|'
             r'codesize|codecopy|gasprice|extcodesize|extcodecopy|'
             r'blockhash|coinbase|timestamp|number|difficulty|gaslimit|'
             r'pop|mload|mstore|mstore8|sload|sstore|for|switch|'
             r'jump|jumpi|pc|msize|gas|jumpdest|push1|push2|'
             r'push32|dup1|dup2|dup16|swap1|swap2|swap16|log0|log1|log4|'
             r'create|call|callcode|return|delegatecall|suicide|'
             r'returndatasize|returndatacopy|staticcall|revert|'
             r'invalid)\b',
             Name.Function),

            # everything else is either a local/external var, or label
            ('[a-zA-Z_]\w*', Name)
        ],
        # TODO: Yul parsing (not implemented ATM)
        #'yul': [],
        'comment-parse-single': [
            include('natspec'),
            (r'\n', Comment.Single, '#pop'),
            (r'[^\n]', Comment.Single),
        ],
        'comment-parse-multi': [
            include('natspec'),
            (r'[^*/]', Comment.Multiline),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        'comments': [
            (r'//', Comment.Single, 'comment-parse-single'),
            (r'/[*]', Comment.Multiline, 'comment-parse-multi'),
        ],
        'keywords-builtins': [
            # compiler built-ins
            (r'(balance|now)\b', Name.Builtin),
            (r'selector\b', Name.Builtin),
            (r'(super|this)\b', Name.Builtin),
        ],
        'keywords-functions': [
            # receive/fallback functions
            (r'(receive|fallback)\b', Keyword.Function),

            # like block.hash and msg.gas in `keywords-nested`
            (r'(blockhash|gasleft)\b', Name.Function),

            # single-instruction yet function syntax
            (r'(selfdestruct|suicide)\b', Name.Function),

            # processed into many-instructions
            (r'(send|transfer|call|callcode|delegatecall)\b',
             Name.Function),
            (r'(assert|revert|require)\b', Name.Function),
            (r'push\b', Name.Function),

            # built-in functions and/or precompiles
            (words(('addmod', 'ecrecover', 'keccak256', 'mulmod',
                    'sha256', 'sha3', 'ripemd160'),
                   suffix=r'\b'), Name.Function),
        ],
        'keywords-types': [
            (words(('address', 'bool', 'byte', 'bytes', 'int', 'string',
                    'uint'),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names('bytes', range(1, 32+1)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names('int', range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),
            (words(type_names('uint', range(8, 256+1, 8)),
                   suffix=r'\b'), Keyword.Type),

            # not yet fully implemented, therefore reserved types
            (words(('fixed', 'ufixed'), suffix=r'\b'), Keyword.Reserved),
            (words(type_names_mn('fixed',
                                 range(8, 256+1, 8),
                                 range(0, 80+1, 1)),
                   suffix=r'\b'), Keyword.Reserved),
            (words(type_names_mn('ufixed',
                                 range(8, 256+1, 8),
                                 range(0, 80+1, 1)),
                   suffix=r'\b'), Keyword.Reserved),
        ],
        'keywords-nested': [
            (r'abi\.encode(|Packed|WithSelector|WithSignature)\b',
             Name.Builtin),
            (r'block\.(blockhash|coinbase|difficulty|gaslimit|hash|'
             r'number|timestamp)\b', Name.Builtin),
            (r'msg\.(data|gas|sender|value)\b', Name.Builtin),
            (r'tx\.(gasprice|origin)\b', Name.Builtin),
        ],
        'keywords-other': [
            (words(('for', 'in', 'while', 'do', 'break', 'return',
                    'returns', 'continue', 'if', 'else', 'throw',
                    'new', 'delete', 'try', 'catch'),
                   suffix=r'\b'), Keyword),

            (r'assembly\b', Keyword, 'assembly'),

            (words(('contract', 'interface', 'enum', 'event', 'function',
                    'constructor', 'library', 'mapping', 'modifier',
                    'struct', 'var'),
                   suffix=r'\b'), Keyword.Declaration),

            (r'(import|using)\b', Keyword.Namespace),

            # pragmas are not pragmatic in their formatting :/
            (r'pragma( experimental| solidity|)\b', Keyword),
            # misc keywords
            (r'(_|as|constant|from|is)\b', Keyword),
            (r'emit\b', Keyword),
            # built-in modifier
            (r'payable\b', Keyword),
            # variable location specifiers
            (r'(calldata|memory|storage)\b', Keyword),
            # method visibility specifiers
            (r'(external|internal|private|public)\b', Keyword),
            # event parameter specifiers
            (r'(anonymous|indexed)\b', Keyword),
            # added in solc v0.4.0, not covered elsewhere
            (r'(abstract|pure|static|view)\b', Keyword),
            # added in solc v0.6.0, not covered elsewhere
            (r'(override|virtual)\b', Keyword),
            # access to contracts' codes and name
            (r'type\(.*\)\.(creationCode|runtimeCode|name)\b', Keyword),

            # reserved for future use since don't-remember-when
            (words(('after', 'case', 'default', 'final', 'in', 'inline',
                    'let', 'match', 'null', 'of', 'relocatable', 'static',
                    'switch', 'typeof'),
                   suffix=r'\b'), Keyword.Reserved),
            # reserved for future use since solc v0.5.0
            (words(('alias', 'apply', 'auto', 'copyof', 'define',
                    'immutable', 'implements', 'macro', 'mutable',
                    'partial', 'promise', 'reference',
                    'sealed', 'sizeof', 'supports', 'typedef',
                    'unchecked'),
                   suffix=r'\b'), Keyword.Reserved),

            # built-in constants
            (r'(true|false)\b', Keyword.Constant),
            (r'(wei|finney|szabo|ether)\b', Keyword.Constant),
            (r'(seconds|minutes|hours|days|weeks|years)\b',
             Keyword.Constant),
        ],
        'natspec': [
            (r'@(author|dev|notice|param|return|title)\b',
             Comment.Special),
        ],
        'numbers': [
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?', Number.Float),
            (r'[0-9]+([eE][0-9]+)?', Number.Integer),
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
            include('keywords-builtins'),
            include('keywords-functions'),
            include('keywords-types'),
            include('keywords-nested'),
            include('keywords-other'),
            include('numbers'),
            include('strings'),
            include('whitespace'),

            (r'\+\+|--|\*\*|\?|:|~|&&|\|\||=>|==?|!=?|'
             r'(<<|>>>?|[-<>+*%&|^/])=?', Operator),

            (r'[{(\[;,]', Punctuation),
            (r'[})\].]', Punctuation),

            # everything else is a var/function name
            ('[a-zA-Z$_]\w*', Name)
        ] # 'root'
    } # tokens

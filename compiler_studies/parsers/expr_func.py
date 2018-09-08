'''

What would a LL(1) grammar with function calls look like?

Adding func calls:

<Goal>     ::= <Expr>

<Expr>     ::= <Term> <Expr'>

<Expr'>    ::= + <Term> <Expr'>
            |  - <Term> <Expr'>
            |  $

<Term>     ::= <Factor> <Term'>

<Term'>    ::= * <Factor> <Term'>
            |  / <Factor> <Term'>
            |  $

<Factor>   ::= ( <Expr> )
            |  <Atom>

<Atom>     ::= name <Atom'>
            |  num

<Atom'>    ::= ( <Args> )
            |  $

<Args>     ::= <Expr> <MoreArgs>
            | $

<MoreArgs> ::= , <Expr>
            | $
'''

from compiler_studies.scanners import scanner1


class ASTNode:
    def __init__(self, type, children=None):
        self.type = type
        self.children = children or []

    def __str__(self):
        return '<{}>'.format(self.type)

class InvalidSyntax(Exception):
    pass


def next_word():
    global word
    if not is_eof():
        try:
            word = next(words)
        except StopIteration:
            word = '$'
    else:
        raise InvalidSyntax('Incomplete program')

def is_eof():
    return word == '$'

def expr():
    return ASTNode(
        'Expr',
        [term(), expr_prime()]
    )

def expr_prime():
    if is_eof():
        return ASTNode(
            'Expr\'',
            [word],
        )
    elif word.type in '+-':
        w = word
        next_word()
        return ASTNode(
            'Expr\'',
            [w, term(), expr_prime()],
        )
    else:
        # Matching $: do nothing. Let the next recursive call consume the current token
        pass

def term():
    return ASTNode(
        'Term',
        [factor(), term_prime()],
    )

def term_prime():
    if is_eof():
        return ASTNode(
            'Term\'',
            [word],
        )
    elif word.type in '*/':
        w = word
        next_word()
        return ASTNode(
            'Term\'',
            [w, factor(), term_prime()],
        )
    else:
        # Matching $: do nothing. Let the next recursive call consume the current token
        pass

def factor():
    if word.type == '(':
        next_word()
        e = expr()

        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next_word()
        return ASTNode(
            'Factor',
            ['(', e, ')'],
        )
    else:
        return ASTNode(
            'Factor',
            [atom()],
        )

def atom():
    if word.type == 'num':
        w = word
        next_word()
        return ASTNode(
            'Atom',
            [w],
        )

    elif word.type == 'name':
        w = word
        next_word()
        return ASTNode(
            'Atom',
            [w, atom_prime()],
        )

def atom_prime():
    if word.type == '(':
        w = word
        next_word()
        # parse arg list
        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        return ASTNode(
            'Atom\'',
            [],
        )
    else:
        pass

def pprint(node, indent=0):
    print('{}{}'.format('\t'*indent, node))
    if isinstance(node, ASTNode):
        for child in node.children:
            pprint(child, indent+1)

word = None
words = None

def main():
    prog = '5 * (b + c())'
    lexemes = scanner1.scan(prog)

    global words
    words = iter(lexemes)
    next_word()
    e = expr()
    pprint(e)

if __name__ == '__main__':
    main()
'''

What would a LL(1) grammar with function calls look like?

Adding func calls and assignment:

# Note that while semantically it doesn't make much sense for the goal
# to be "an Asgn" (for assignment expression), I will leave it for now,
# as it make the rest of the parser.

# One suggestion to mend this is to transform:
# Asgn => Expr
# Expr => MathExpr

# Also, node that it only makes sense to assign to a `name`, which is
# only a particular case of Expr; This can be handled in later stages,
# for example reporting a syntax error when building the AST out of the
# "expression AST". Or when emiting the opcodes/interpreting the AST.


<Goal>     ::= <Asgn>

<Asgn>     ::= <Expr> <Asng'>

<Asgn'>    ::= = <Expr>
            |  $

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
            |  string

<Atom'>    ::= ( <Args> )
            |  $

<Args>     ::= <Expr> <MoreArgs>
            | $

<MoreArgs> ::= , <Expr> <MoreArgs>
            | $
'''

from compiler_studies.scanners import scanner1


class ASTNode:
    _id = 0

    def __init__(self, type, children=None):
        self.id = ASTNode._id
        ASTNode._id += 1

        self.type = type

        # Filter out production rules -> $
        self.children = [c for c in children if c is not None] or []

    def __str__(self):
        return '<{}:{}>'.format(self.id, self.type)


class ASTLeaf(ASTNode):
    def __init__(self, value):
        self.id = ASTNode._id
        ASTNode._id += 1

        self.value = value
        self.children = []

    def __str__(self):
        return '<{}: {}>'.format(self.id, self.value)


class InvalidSyntax(Exception):
    pass


def next_word():
    global word
    if word is None or not is_eof():
        try:
            word = next(words)
        except StopIteration:
            word = scanner1.Lexeme('$', '$')
    else:
        raise InvalidSyntax('Incomplete program')

def is_eof():
    return word.type == '$'


def asgn():
    return ASTNode(
        'Asgn',
        [expr(), asgn_prime()],
    )

def asgn_prime():
    if word.type == '=':
        next_word()
        return ASTNode(
            'Asgn\'',
            [ASTLeaf('='), expr()],
        )
    else:
        return None

def expr():
    return ASTNode(
        'Expr',
        [term(), expr_prime()]
    )

def expr_prime():
    if is_eof():
        return ASTNode(
            'Expr\'',
            [ASTLeaf(word)],
        )
    elif word.type in '+-':
        w = word
        next_word()
        return ASTNode(
            'Expr\'',
            [ASTLeaf(w), term(), expr_prime()],
        )
    else:
        # Matching $: do nothing. Let the next recursive call consume the current token
        return None

def term():
    return ASTNode(
        'Term',
        [factor(), term_prime()],
    )

def term_prime():
    if is_eof():
        return ASTNode(
            'Term\'',
            [ASTLeaf(word)],
        )
    elif word.type in '*/':
        w = word
        next_word()
        return ASTNode(
            'Term\'',
            [ASTLeaf(w), factor(), term_prime()],
        )
    else:
        return None

def factor():
    if word.type == '(':
        next_word()
        e = expr()

        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next_word()
        return ASTNode(
            'Factor',
            [ASTLeaf('('), e, ASTLeaf(')')],
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
            [ASTLeaf(w)],
        )

    if word.type == 'string':
        w = word
        next_word()
        return ASTNode(
            'Atom',
            [ASTLeaf(w)],
        )

    elif word.type == 'name':
        w = word
        next_word()
        return ASTNode(
            'Atom',
            [ASTLeaf(w), atom_prime()],
        )

def atom_prime():
    if word.type == '(':
        w = word
        next_word()
        a = args()
        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next_word()
        return ASTNode(
            'Atom\'',
            [ASTLeaf('('), a, ASTLeaf(')')],
        )
    else:
        return None

def args():
    return ASTNode(
        'Args',
        [expr(), more_args()],
    )

def more_args():
    if is_eof():
        return ASTNode(
            'MoreArgs',
            [ASTLeaf(word)],
        )

    elif word.type == ',':
        w = word
        next_word()
        return ASTNode(
            'MoreArgs',
            [ASTLeaf(w), expr(), more_args()]
        )

    else:
        return None


def pprint(node, indent=0):
    print('{}{}'.format('\t'*indent, node))
    if isinstance(node, ASTNode):
        for child in node.children:
            pprint(child, indent+1)

def print_dot(node):

    def inner(node):
        for child in node.children:
            print('"{}" -> "{}";'.format(node, child))
            if child:
                inner(child)

    print('digraph G {')
    inner(node)
    print('}')


word = None
words = None


def main():
    prog = '''
    a = b + func(1 + len('hello, ' + 'world'), c)
    '''
    lexemes = scanner1.scan(prog)

    global words
    words = iter(lexemes)
    next_word()
    e = asgn()

    if not is_eof():
        raise InvalidSyntax('Leftover starting with {}'.format(word))

    #pprint(e)
    print_dot(e)

if __name__ == '__main__':
    main()

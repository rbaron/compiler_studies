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


class ASTLeaf:
    def __init__(self, value):
        self.id = ASTNode._id
        ASTNode._id += 1

        self.value = value

    def __str__(self):
        return '<{}: {}>'.format(self.id, self.value)


class FunCall:
    def __init__(self, name, args):
        self.id = ASTNode._id
        ASTNode._id += 1
        self.name = name
        self.args = args

    def __str__(self):
        return '<{}: FunCall {} - {} args>'.format(self.id, self.name, len(self.args))


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
    e = expr()
    prime = asgn_prime()

    if asgn_prime is not None:
        return ASTNode(
            '=',
            [e, prime]
        )
    else:
        return e

def asgn_prime():
    if word.type == '=':
        next_word()
        return expr()
    else:
        return None

def expr():
    t = term()
    prime = expr_prime()

    if prime is not None:
        prime.children = [t] + prime.children
        return prime
    else:
        return t

def expr_prime():
    if word.type in '+-':
        w = word
        next_word()
        t = term()
        prime = expr_prime()

        if prime is not None:
            prime.children = [t] + prime.children
            return ASTNode(
                w.type,
                [prime]
            )

        else:
            return ASTNode(
                w.type,
                [t]
            )

    return None

def term():
    f = factor()
    prime = term_prime()

    if prime is not None:
        prime.children = [f] + prime.children
        return prime

    else:
        return f

def term_prime():
    if word.type in '*/':
        w = word
        next_word()

        f = factor()
        prime = term_prime()

        if prime is not None:
            prime.children = [t] + prime.children
            return ASTNode(
                w.type,
                [prime]
            )

        else:
            return ASTNode(
                w.type,
               [f]
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
        return e
    else:
        return atom()

def atom():
    if word.type == 'num':
        w = word
        next_word()
        return ASTLeaf(w)

    if word.type == 'string':
        w = word
        next_word()
        return ASTLeaf(w)

    elif word.type == 'name':
        w = word
        next_word()

        prime = atom_prime()

        if prime is not None:
            return FunCall(
                w.value,
                prime,
            )

        # Var lookup
        else:
            return ASTLeaf(
                'VarLookup {}'.format(w.value),
            )
    else:
        return None

def atom_prime():
    if word.type == '(':
        w = word
        next_word()
        a = args()
        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next_word()

        return a
    else:
        return None

def args():
    arglist = []

    a = expr()
    while a is not None:
        arglist.append(a)
        a = more_args()

    return arglist

def more_args():
    if word.type == ',':
        w = word
        next_word()

        return expr()

    else:
        return None


def pprint(node, indent=0):
    print('{}{}'.format('\t'*indent, node))
    if isinstance(node, ASTNode):
        for child in node.children:
            pprint(child, indent+1)

def print_dot(node):

    def inner(node):
        if not isinstance(node, ASTNode):
            return

        for child in node.children:
            print('"{}" -> "{}";'.format(node, child))
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

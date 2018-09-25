'''

<Goal>      ::= <Stmts>

<Stmts>     ::= <Stmt> <MoreStmts>

<MoreStmts> ::= <Stmt> <MoreStmts>
             |  $

<Stmt>      ::= <IfElse>
             |  <FunDef>
             |  <Return>
             |  <Asgn>

<IfElse>    ::= if <Expr> { <Stmts> } else { <Stmts> }

<FunDef>    ::= fun <ArgList> { <Stmts> }

<Return>    ::= return <Expr>

<ArgList>   ::= ( name <MoreNames> )

<MoreNames> ::= , name <MoreAtoms>
             |  $

<Asgn>      ::= <Expr> <Asng'>

<Asgn'>     ::= = <Expr>
             |  $

<Expr>      ::= <Term> <Expr'>

<Expr'>     ::= + <Term> <Expr'>
             |  - <Term> <Expr'>
             |  $

<Term>      ::= <Factor> <Term'>

<Term'>     ::= * <Factor> <Term'>
             |  / <Factor> <Term'>
             |  $

<Factor>    ::= ( <Expr> )
             |  <Atom>

<Atom>      ::= name <Atom'>
             |  num
             |  string

<Atom'>     ::= ( <Args> )
             |  $

<Args>      ::= <Expr> <MoreArgs>
             | $

<MoreArgs>  ::= , <Expr> <MoreArgs>
             | $
'''

from compiler_studies.scanners import scanner1


word = None
words = None


class Node:
    __counter = 0

    def __init__(self):
        self.id = Node.__counter
        Node.__counter += 1

    def __str__(self):
        return '<{} {}>'.format(self.id, self.__class__.__name__)


class ASTNode(Node):
    def __init__(self, type, children=None):
        super().__init__()
        self.type = type

        # Filter out production rules -> $
        self.children = [c for c in children if c is not None] or []

    def __str__(self):
        return '<{}:{}>'.format(self.id, self.type)


class ASTLeaf(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Atom(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return '<{} {} {}>'.format(self.id, type(self).__name__, self.value)


class Num(Atom):
    def __init__(self, value):
        super().__init__(value)


class String(Atom):
    def __init__(self, value):
        super().__init__(value)


class VarLookup(Atom):
    def __init__(self, value):
        super().__init__(value)


class FunCall(Node):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

    def __str__(self):
        return '<{} FunCall {} | {} args>'.format(self.id, self.name, len(self.args))

    @property
    def children(self):
        return self.args


class IfElse(Node):
    def __init__(self, cond, cons, alt):
        super().__init__()
        self.cond = cond
        self.cons = cons
        self.alt = alt

    def __str__(self):
        return '<{} IfElse>'.format(self.id)

    @property
    def children(self):
        return [self.cond, self.cons, self.alt]


class FunDef(Node):
    def __init__(self, name, args, body):
        super().__init__()
        self.name = name
        self.args = args
        self.body = body

    def __str__(self):
        return '<{} FunDef {} ({})>'.format(self.id, self.name, self.args)

    @property
    def children(self):
        return [self.body]


class Return(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class Stmts(Node):
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts

    def __str__(self):
        return '<{} Stmts>'.format(self.id)

    @property
    def children(self):
        return self.stmts


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

def test(expected_word):
    if word.value != expected_word:
        raise InvalidSyntax('Expected {}, found {}'.format(expected_word, word.value))


def next_and_test(expected_word):
    next_word()
    test(expected_word)


def is_eof():
    return word.type == '$'


def stmts():
    lst = []

    s = stmt()

    if s is None:
        raise InvalidSyntax('Invalid statement {}'.format(word))

    while s is not None:
        lst.append(s)
        s = morestmts()

    return Stmts(lst)


def morestmts():
    # Bit of hand-waving here:
    # When parsing a block like this:
    # fun hello_world() {
    #   say_hello()
    #   say_world()
    # }
    #
    # The guts of the function contains multiple statements.
    # We're looking ahead here so we don't try to parse the
    # closing } as a statement. Same for $ in the top level.
    if word.type in '$}':
        return None

    return stmt()


def stmt():
    ie = ifelse()
    if ie is not None:
        return ie

    f = fundef()
    if f is not None:
        return f

    r = ret()
    if r is not None:
        return r

    a = asgn()
    if a is not None:
        return a

    raise InvalidSyntax('Unable to parse statement')


def ret():
    if word.value != 'return':
        return None

    next_word()
    e = expr()

    return Return(e)


def ifelse():
    if word.value != 'if':
        return None

    next_word()
    cond = expr()

    if cond is None:
        raise InvalidSyntax('Unable to parse condition')

    test('{')

    next_word()
    cons = stmts()

    test('}')
    next_and_test('else')
    next_and_test('{')

    next_word()
    alt = stmts()

    test('}')

    next_word()

    return IfElse(cond, cons, alt)


def fundef():
    if word.value != 'fun':
        return None

    next_word()
    name = word.value
    next_word()
    args = arglist()
    next_and_test('{')
    next_word()
    body = stmts()
    test('}')

    next_word()

    return FunDef(name, args, body)


def arglist():
    if word.type != '(':
        raise InvalidSyntax('Expected (, found {}'.format(word.type))

    next_word()

    if word.type != 'name':
        raise InvalidSyntax('Expected name, found {}'.format(word.type))

    args = [word.value]

    next_word()
    more = morenames()
    while more is not None:
        args.append(more)
        more = morenames()

    if word.type != ')':
        raise InvalidSyntax('Expected ), found {}'.format(word.type))

    return args


def morenames():
    if word.type != ',':
        return None

    next_word()

    if word.type != 'name':
        raise InvalidSyntax('Expected name, found {}'.format(word.type))

    name = word.value
    next_word()
    return name


def asgn():
    e = expr()
    prime = asgn_prime()

    if prime is not None:
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
        return Num(w.value)

    if word.type == 'string':
        w = word
        next_word()
        return String(w.value)

    elif word.type == 'name':
        w = word
        next_word()

        prime = atom_prime()

        # Function call
        if prime is not None:
            return FunCall(
                w.value,
                prime,
            )

        # Variable lookup
        else:
            return VarLookup(w.value)

    raise InvalidSyntax('Unable to parse atom {}'.format(word.value))


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
        a = moreargs()

    return arglist


def moreargs():
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
        if not hasattr(node, 'children'):
            print('"{}";'.format(node))
            return

        for child in node.children:
            print('"{}" -> "{}";'.format(node, child))
            inner(child)

    print('digraph G {')
    inner(node)
    print('}')


def main():
    prog = '''
    fun func (n) {
        c = n + 42
        a b
        return c
    }

    if 1 + 2 {
        print('yes')
    } else {
        print('no')
    }

    a = b + func(1 + len('hello, ' + 'world'), c)
    '''

    lexemes = scanner1.scan(prog)

    global words
    words = iter(lexemes)
    next_word()
    s = stmts()

    if not is_eof():
        raise InvalidSyntax('Leftover starting with {}'.format(word))

    #pprint(e)
    print_dot(s)

if __name__ == '__main__':
    main()

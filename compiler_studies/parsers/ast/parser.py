'''

<Goal>      ::= <Stmts>

<Stmts>     ::= <Stmt> <MoreStmts>

<MoreStmts> ::= <Stmt> <MoreStmts>
             |  $

<Stmt>      ::= <IfElse>
             |  <FunDef>
             |  <Return>
             |  <Asgn>
             |  <Comment>

<IfElse>    ::= if <Expr> { <Stmts> } else { <Stmts> }

<FunDef>    ::= fun <ArgList> { <Stmts> }

<Return>    ::= return <Expr>

<ArgList>   ::= ( name <MoreNames> )

<MoreNames> ::= , name <MoreAtoms>
             |  $

<Comment>   ::= comment

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


class Comment(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


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


def stmts(stream):
    lst = []

    s = stmt(stream)

    if s is None:
        raise InvalidSyntax('Invalid statement {}'.format(word))

    while s is not None:
        lst.append(s)
        s = morestmts(stream)

    return Stmts(lst)


def morestmts(stream):
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
    if stream.head.type in '$}':
        return None

    return stmt(stream)


def stmt(stream):
    if stream.head.type == 'comment':
        w = stream.head
        next(stream)
        return Comment(w.value)

    ie = ifelse(stream)
    if ie is not None:
        return ie

    f = fundef(stream)
    if f is not None:
        return f

    r = ret(stream)
    if r is not None:
        return r

    a = asgn(stream)
    if a is not None:
        return a

    raise InvalidSyntax('Unable to parse statement')


def ret(stream):
    if stream.head.value != 'return':
        return None

    next(stream)
    e = expr(stream)

    return Return(e)


def ifelse(stream):
    if stream.head.value != 'if':
        return None

    next(stream)
    cond = expr(stream)

    if cond is None:
        raise InvalidSyntax('Unable to parse condition')

    stream.test('{')

    next(stream)
    cons = stmts(stream)

    stream.test('}')
    stream.next_and_test('else')
    stream.next_and_test('{')

    next(stream)
    alt = stmts(stream)

    stream.test('}')

    next(stream)

    return IfElse(cond, cons, alt)


def fundef(stream):
    if stream.head.value != 'fun':
        return None

    next(stream)
    name = stream.head.value
    next(stream)
    args = arglist(stream)
    stream.next_and_test('{')
    next(stream)
    body = stmts(stream)
    stream.test('}')

    next(stream)

    return FunDef(name, args, body)


def arglist(stream):
    if stream.head.type != '(':
        raise InvalidSyntax('Expected (, found {}'.format(word.type))

    next(stream)

    if stream.head.type != 'name':
        raise InvalidSyntax('Expected name, found {}'.format(word.type))

    args = [stream.head.value]

    next(stream)
    more = morenames(stream)
    while more is not None:
        args.append(more)
        more = morenames(stream)

    if stream.head.type != ')':
        raise InvalidSyntax('Expected ), found {}'.format(word.type))

    return args


def morenames(stream):
    if stream.head.type != ',':
        return None

    next(stream)

    if stream.head.type != 'name':
        raise InvalidSyntax('Expected name, found {}'.format(word.type))

    name = stream.head.value
    next(stream)
    return name


def asgn(stream):
    e = expr(stream)
    prime = asgn_prime(stream)

    if prime is not None:
        return ASTNode(
            '=',
            [e, prime]
        )
    else:
        return e


def asgn_prime(stream):
    if stream.head.type == '=':
        next(stream)
        return expr(stream)
    else:
        return None


def expr(stream):
    t = term(stream)
    prime = expr_prime(stream)

    if prime is not None:
        prime.children = [t] + prime.children
        return prime
    else:
        return t


def expr_prime(stream):
    if stream.head.type in '+-':
        w = stream.head
        next(stream)
        t = term(stream)
        prime = expr_prime(stream)

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


def term(stream):
    f = factor(stream)
    prime = term_prime(stream)

    if prime is not None:
        prime.children = [f] + prime.children
        return prime

    else:
        return f


def term_prime(stream):
    if stream.head.type in '*/':
        w = stream.head
        next(stream)

        f = factor(stream)
        prime = term_prime(stream)

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


def factor(stream):
    if stream.head.type == '(':
        next(stream)
        e = expr(stream)

        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next(stream)
        return e
    else:
        return atom(stream)


def atom(stream):
    if stream.head.type == 'num':
        w = stream.head
        next(stream)
        return Num(w.value)

    if stream.head.type == 'string':
        w = stream.head
        next(stream)
        return String(w.value)

    elif stream.head.type == 'name':
        w = word
        w = stream.head
        next(stream)

        prime = atom_prime(stream)

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


def atom_prime(stream):
    if stream.head.type == '(':
        w = stream.head
        next(stream)
        a = args(stream)
        if stream.head.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)

        next(stream)

        return a
    else:
        return None


def args(stream):
    arglist = []

    a = expr(stream)
    while a is not None:
        arglist.append(a)
        a = moreargs(stream)

    return arglist


def moreargs(stream):
    if stream.head.type == ',':
        w = stream.head
        next(stream)

        return expr(stream)

    else:
        return None


parse = stmts


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


class Stream:
    def __init__(self, lexemes):
        self.iter = iter(lexemes)
        self.head = None
        next(self)

    def __next__(self):
        if self.head is None or not self.is_eof():
            try:
                self.head = next(self.iter)
            except StopIteration:
                self.head = scanner1.Lexeme('$', '$')

            return self.head
        else:
            raise InvalidSyntax('Incomplete program')

    def __iter__(self):
        return self

    def test(self, expected_value):
        if self.head.value != expected_value:
            raise InvalidSyntax('Expected {}; found {}'.format(expected_value, self.head.value))

    def next_and_test(self, value):
        next(self)
        self.test(value)

    def is_eof(self):
        return self.head.type == '$'


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

    stream = Stream(lexemes)
    s = parse(stream)

    if not stream.is_eof():
        raise InvalidSyntax('Leftover starting with {}'.format(word))

    #pprint(e)
    print_dot(s)


if __name__ == '__main__':
    main()

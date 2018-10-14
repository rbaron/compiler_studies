from compiler_studies.no_loop import scanner


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
    def __init__(self, expr, args):
        super().__init__()
        self.expr = expr
        self.args = args

    def __str__(self):
        return '<{} FunCall {} | {} args>'.format(self.id, self.expr, len(self.args))

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


class LambDef(Node):
    def __init__(self, args, body):
        super().__init__()
        self.args = args
        self.body = body

    def __str__(self):
        return '<{} LambDef ({})>'.format(self.id, self.args)

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
        raise InvalidSyntax('Invalid statement {}'.format(stream.head))

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
    cond = comp(stream)

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


def argsdef(stream):
    if stream.head.type != '(':
        raise InvalidSyntax('Expected (, found {}'.format(stream.head.type))

    next(stream)

    args = argsnames(stream) or []

    if stream.head.type != ')':
        raise InvalidSyntax('Expected ), found {}'.format(stream.head.type))

    next(stream)
    return args


def argsnames(stream):
    if stream.head.type != 'name':
        return None

    args = [stream.head.value]
    next(stream)

    more = morenames(stream)
    while more is not None:
        args.append(more)
        more = morenames(stream)

    return args


def morenames(stream):
    if stream.head.type != ',':
        return None

    next(stream)

    if stream.head.type != 'name':
        raise InvalidSyntax('Expected name, found {}'.format(stream.head.type))

    name = stream.head.value
    next(stream)
    return name


def asgn(stream):
    e = comp(stream)
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
        return comp(stream)
    else:
        return None


def comp(stream):
    e = expr(stream)
    prime = comp_prime(stream)

    if prime is not None:
        prime.children = [e] + prime.children
        return prime
    else:
        return e


def comp_prime(stream):
    if stream.head.value in ['==', '<=', '>=']:
        w = stream.head
        next(stream)
        e = expr(stream)

        return ASTNode(w.type, [e])

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
        e = comp(stream)

        if stream.head.type != ')':
            raise InvalidSyntax('Expected ), found', stream.head.type)

        next(stream)
        return e
    else:
        return atomcalls(stream)


def atomcalls(stream):
    node = atom(stream)

    for a in callsargs(stream):
        node = FunCall(node, a)

    return node


def callsargs(stream):
    all_allsargs = []

    while stream.head.type == '(':

        next(stream)

        all_allsargs.append(args(stream))

        if stream.head.type != ')':
            raise InvalidSyntax('Expected ), found', stream.head.type)

        next(stream)

    return all_allsargs


def atom(stream):
    lamb = lambdef(stream)
    if lamb is not None:
        return lamb

    elif stream.head.type == 'num':
        w = stream.head
        next(stream)
        return Num(w.value)

    elif stream.head.type == 'string':
        w = stream.head
        next(stream)
        return String(w.value)

    elif stream.head.type == 'name':
        w = stream.head
        next(stream)

        return VarLookup(w.value)

    raise InvalidSyntax('Unable to parse atom {}'.format(stream.head.value))


def args(stream):
    if stream.head.type == ')':
        return []

    arglist = []

    a = comp(stream)
    while a is not None:
        arglist.append(a)
        a = moreargs(stream)

    return arglist


def moreargs(stream):
    if stream.head.type == ',':
        w = stream.head
        next(stream)

        return comp(stream)

    else:
        return None


def lambdef(stream):
    if stream.head.value != '\\':
        return None

    next(stream)
    al = argsdef(stream)
    stream.test('{')
    next(stream)
    ss = stmts(stream)
    stream.test('}')
    next(stream)
    return LambDef(al, ss)


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
                self.head = scanner.Lexeme('$', '$')

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
    func = \(n) {
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

    lexemes = scanner.scan(prog)

    stream = Stream(lexemes)
    s = parse(stream)

    if not stream.is_eof():
        raise InvalidSyntax('Leftover starting with {}'.format(stream.head))

    #pprint(e)
    print_dot(s)


if __name__ == '__main__':
    main()

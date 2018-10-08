from compiler_studies.add_mult import scanner


class Stream:
    '''A buffer with a lookahead of 1'''

    def __init__(self, lst):
        self._iter = iter(lst)

        self.is_empty = False
        self.head = next(self)

    def __next__(self):
        try:
            self.head = next(self._iter)
        except StopIteration:
            if self.is_empty:
                raise
            else:
                self.is_empty = True
        return self.head


class ExprNode:
    __counter = 0
    def __init__(self, type, children=None):
        self.id = ExprNode.__counter
        ExprNode.__counter += 1

        self.type = type
        self.children = [c for c in children if c is not None] if children else []

    def __str__(self):
        return '"{}" [label = "{}"]'.format(self.id, self.type)


class ExprLeaf(ExprNode):
    def __init__(self, value):
        super().__init__('Leaf')
        self.value = value

    def __str__(self):
        return '"{}" [label = "{}"]'.format(self.id, self.value)


def expr(stream):
    parsed_term = term(stream)
    parsed_prime = expr_prime(stream)
    return ExprNode('Expr', [parsed_term, parsed_prime])


def expr_prime(stream):
    if stream.head.value != '+':
        return None

    next(stream)
    parsed_term = term(stream)
    parsed_expr_prime = expr_prime(stream)
    return ExprNode('Expr\'', [ExprLeaf('+'), parsed_term, parsed_expr_prime])


def term(stream):
    parsed_factor = factor(stream)
    parsed_prime = term_prime(stream)

    return ExprNode('Term', [parsed_factor, parsed_prime])


def term_prime(stream):
    if stream.head.value != '*':
        return None

    next(stream)
    parsed_factor = factor(stream)
    parsed_prime = term_prime(stream)
    return ExprNode('Term\'', [ExprLeaf('*'), parsed_factor, parsed_prime])


def factor(stream):
    if stream.head.type == 'number':
        leaf = ExprLeaf(stream.head.value)
        next(stream)
        return leaf

    elif stream.head.value == '(':
        next(stream)
        parsed_expr = expr(stream)
        assert stream.head.value == ')', stream.head.value
        next(stream)
        return ExprNode('Expr', [ExprLeaf('('), parsed_expr, ExprLeaf(')')])

    else:
        raise ValueError('Invalid factor token: {}'.format(stream.head.value))


def print_dot(node):
    def inner(node):
        if not isinstance(node, ExprNode):
            print('{};'.format(node))
            return
        print('{};'.format(node))

        for child in node.children:
            print('{} -> {};'.format(node.id, child.id))
            inner(child)

    print('digraph G {')
    inner(node)
    print('}')


def test():
    string = '''
        1 + 2 * (3 + 4 + 5 * 2)
    '''

    stream = Stream(scanner.scan(string))
    parsed_expr = expr(stream)

    if not stream.is_empty:
        raise ValueError('Stream hasn\'t been fully consumed {}'.format(stream.head.value))

    print_dot(parsed_expr)


if __name__ == '__main__':
    test()

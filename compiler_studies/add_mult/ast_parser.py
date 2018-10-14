import sys

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


class ASTNode:
    _counter = 0
    def __init__(self, op, left, right):
        self.id = ASTNode._counter
        ASTNode._counter += 1

        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return '"{}" [label = "{}"]'.format(self.id, self.op)


class ASTLeaf:
    def __init__(self, value):
        self.id = ASTNode._counter
        ASTNode._counter += 1

        self.value = value

    def __str__(self):
        return '"{}" [label = "{}"]'.format(self.id, self.value)


def expr(stream):
    parsed_term = term(stream)
    parsed_prime = expr_prime(stream)

    if parsed_prime is not None:
        return ASTNode('+', parsed_term, parsed_prime)
    else:
        return parsed_term


def expr_prime(stream):
    if stream.head.value != '+':
        return None

    next(stream)
    parsed_term = term(stream)
    parsed_prime = expr_prime(stream)

    if parsed_prime is not None:
        return ASTNode('+', parsed_term, parsed_prime)
    else:
        return parsed_term


def term(stream):
    parsed_factor = factor(stream)
    parsed_prime = term_prime(stream)

    if parsed_prime is not None:
        return ASTNode('*', parsed_factor, parsed_prime)
    else:
        return parsed_factor


def term_prime(stream):
    if stream.head.value != '*':
        return None

    next(stream)
    parsed_factor = factor(stream)
    parsed_prime = term_prime(stream)

    if parsed_prime is not None:
        return ASTNode('*', parsed_factor, parsed_prime)
    else:
        return parsed_factor


def factor(stream):
    if stream.head.type == 'number':
        leaf = ASTLeaf(stream.head.value)
        next(stream)
        return leaf

    elif stream.head.value == '(':
        next(stream)
        parsed_expr = expr(stream)
        assert stream.head.value == ')', stream.head.value
        next(stream)
        return parsed_expr

    else:
        raise ValueError('Invalid factor token: {}'.format(stream.head.value))


parse = expr


def print_dot(node):
    def inner(node):
        if not isinstance(node, ASTNode):
            print('{};'.format(node))
            return
        print('{};'.format(node))

        for child in [node.left, node.right]:
            print('{} -> {};'.format(node.id, child.id))
            inner(child)

    print('digraph G {')
    inner(node)
    print('}')


def test():
    string = sys.argv[1]
    stream = Stream(scanner.scan(string))
    parsed_expr = expr(stream)

    if not stream.is_empty:
        raise ValueError('Stream hasn\'t been fully consumed {}'.format(stream.head.value))

    print_dot(parsed_expr)


if __name__ == '__main__':
    test()

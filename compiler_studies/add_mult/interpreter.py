import sys

from compiler_studies.add_mult import ast_parser, scanner


def eval(node):
    if isinstance(node, ast_parser.ASTLeaf):
        return int(node.value)
    elif isinstance(node, ast_parser.ASTNode):
        left = eval(node.left)
        right = eval(node.right)

        if node.op == '+':
            return left + right
        elif node.op == '*':
            return left * right
        else:
            raise RuntimeError('Unsupported operator: {}'.format(node.op))


def test():
    string = sys.argv[1]
    stream = ast_parser.Stream(scanner.scan(string))
    ast = ast_parser.parse(stream)

    print('Eval\'d to: {}'.format(eval(ast)))


if __name__ == '__main__':
    test()

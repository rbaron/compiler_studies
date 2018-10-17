import argparse

from compiler_studies.no_loop import scanner
from compiler_studies.no_loop import ast_parser as parser


def eval(ast, env):
    if isinstance(ast, parser.Stmts):
        for stmt in ast.stmts:
            if isinstance(stmt, parser.Return):
                return eval(stmt.expr, env)

            # We can return from a if-else block
            elif isinstance(stmt, parser.IfElse):
                ret = eval(stmt, env)
                if ret is not None:
                    return ret
            else:
                eval(stmt, env)

    elif isinstance(ast, parser.ASTNode):
        return eval_astnode(ast, env)

    elif isinstance(ast, parser.VarLookup):
        return env.lookup(ast.value)

    elif isinstance(ast, parser.Num):
        return int(ast.value)

    elif isinstance(ast, parser.String):
        return ast.value

    elif isinstance(ast, parser.IfElse):
        return eval(ast.cons, env) if eval(ast.cond, env) else eval(ast.alt, env)

    elif isinstance(ast, parser.LambDef):
        return Function(ast.args, ast.body, env)

    elif isinstance(ast, parser.FunCall):
        return apply(ast, env)


def eval_astnode(ast, env):
    left, right = ast.children

    if ast.type == '=':
        env[left.value] = eval(right, env)
        return env[left.value]

    elif ast.type == '+':
       return eval(left, env) + eval(right, env)
    elif ast.type == '-':
       return eval(left, env) - eval(right, env)
    elif ast.type == '*':
       return eval(left, env) * eval(right, env)
    elif ast.type == '/':
       return eval(left, env) / eval(right, env)
    elif ast.type == '==':
       return eval(left, env) == eval(right, env)
    elif ast.type == '>=':
       return eval(left, env) >= eval(right, env)
    elif ast.type == '<=':
       return eval(left, env) <= eval(right, env)


def apply(ast, env):
    fun = eval(ast.expr, env)

    args = [eval(a, env) for a in ast.args]

    if isinstance(fun, NativeFunction):
        return fun.callable(*args)

    if len(fun.args) != len(ast.args):
        raise RuntimeError('Wrong number of arguments for {}'.format(ast.name))

    # Augment function environment with arguments
    new_env = Env(fun.env, **{
        name: value
        for (name, value) in zip(fun.args, args)
    })

    ret = eval(fun.body, new_env)

    if ret is None:
        raise RuntimeError('Missing return statement in {}'.format(ast.name))

    return ret


class Function:
    def __init__(self, args, body, env):
        self.args = args
        self.body = body
        self.env = env

    def __repr__(self):
        return '<Function>'


class NativeFunction:
    def __init__(self, name, callable):
        self.name = name
        self.callable = callable


class Env(dict):
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def lookup(self, name):
        if name in self:
            return self[name]
        elif self.parent is not None:
            return self.parent.lookup(name)
        else:
            raise Exception('{} is not defined'.format(name))

    def __repr__(self):
        has_parent = 'Yes' if self.parent is not None else 'No'
        return '<Env has_parent={} {}>'.format(has_parent, super().__repr__())


def parse_args():
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument('files', nargs='+', type=str)
    return argsparser.parse_args()


def main():
    source_files = parse_args().files

    global_env = Env(
        print=NativeFunction('print', print),
    )

    for source_file in source_files:
        with open(source_file) as f:
            stream = parser.Stream(scanner.scan(f.read()))
        ast = parser.parse(stream)
        res = eval(ast, global_env)


if __name__ == '__main__':
    main()

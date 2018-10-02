
from compiler_studies.scanners import scanner1 as scanner
from compiler_studies.parsers.ast import parser


def eval(ast, env):
    #print('Evaling ', ast)
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
        return Function('lambda', ast.args, ast.body, env)

    elif isinstance(ast, parser.FunCall):
        return eval_funcall(ast, env)


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


def eval_funcall(ast, env):
    fun = eval(ast.expr, env)

    args = [eval(a, env) for a in ast.args]

    if isinstance(fun, NativeFunction):
        return fun.callable(*args)

    if len(fun.args) != len(ast.args):
        raise RuntimeError('Wrong number of arguments for {}'.format(ast.name))

    # Augment environment with arguments
    new_env = Env(env, **{
        name: value
        for (name, value) in zip(fun.args, args)
    })

    ret = eval(fun.body, new_env)

    if ret is None:
        raise RuntimeError('Missing return statement in {}'.format(ast.name))

    return ret


class Function:
    def __init__(self, name, args, body, env):
        self.name = name
        self.args = args
        self.body = body
        self.env = env

    def __repr__(self):
        return '<Function {}>'.format(self.name)


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


def main():
    global_env = Env(
        print=NativeFunction('print', print),
    )

    prog = '''
        fib = \(n) {
            if n <= 1 {
                return 1
            } else {
                return fib(n-1) + fib(n-2)
            }
        }

        print('The result is:', fib(5))
    '''
    prog = '''
        a = \() {
            // b = 1 - closure
            return \() { return 1 }
        }
        print(a()())
    '''

    stream = parser.Stream(scanner.scan(prog))
    ast = parser.parse(stream)
    res = eval(ast, global_env)
    print(global_env)


if __name__ == '__main__':
    main()

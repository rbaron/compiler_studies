'''

Classic Expression Grammar, from the book "Engineering a compiler", 2nd edition

Before transforming:

<Goal> ::= <Expr>

<Expr> ::= ( <Expr> )
        |  <Expr> <Op> name
        |  name

<Op>   ::= +
        |  -
        |  *
        |  /

With precedence handling, so that *, / have precedence over +, -:

<Goal> ::= <Expr>

<Expr>   ::= <Expr> + <Term>
          |  <Expr> - <Term>
          |  <Term>

<Term>   ::= <Term> * <Factor>
          |  <Term> / <Factor>
          |  <Factor>

<Factor> ::= ( <Expr> )
          |  num
          |  name

Removing left recursion:

<Goal>   ::= <Expr>

<Expr>   ::= <Term> <Expr'>

<Expr'>  ::= + <Term> <Expr'>
          |  - <Term> <Expr'>
          |  $

<Term>   ::= <Factor> <Term'>

<Term'>  ::= * <Factor> <Term'>
          |  / <Factor> <Term'>
          |  $

<Factor> ::= ( <Expr> )
          |  num
          |  name
'''

class Lexeme:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return '<Lexeme {} {}>'.format(self.type, self.value)

class ASTNode:
    def __init__(self, type, children=None):
        self.type = type
        self.children = children or []

    def __str__(self):
        return '<{}>'.format(self.type)

class InvalidSyntax(Exception):
    pass


# Dummy lexer
def scan(expr):
    lexemes = []
    for char in expr:
        if char >= 'a'  and char <= 'z':
            lexemes.append(Lexeme('name', char))
        elif char in '+-*/()':
            lexemes.append(Lexeme(char, char))
        else:
            pass

    return lexemes

def next_word():
    global word
    if not is_eof():
        try:
            word = next(words)
        except StopIteration:
            word = '$'
    else:
        raise InvalidSyntax('Incomplete program')

def is_eof():
    return word == '$'

def expr():
    return ASTNode(
        'Expr',
        [term(), expr_prime()]
    )

def expr_prime():
    if is_eof():
        return ASTNode(
            'Expr\'',
            [word],
        )
    elif word.type in '+-':
        w = word
        next_word()
        return ASTNode(
            'Expr\'',
            [w, term(), expr_prime()],
        )
    else:
        # Matching $: do nothing. Let the next recursive call consume the current token
        pass

def term():
    return ASTNode(
        'Term',
        [factor(), term_prime()],
    )

def term_prime():
    if is_eof():
        return ASTNode(
            'Term\'',
            [word],
        )
    elif word.type in '*/':
        w = word
        next_word()
        return ASTNode(
            'Term\'',
            [w, factor(), term_prime()],
        )
    else:
        # Matching $: do nothing. Let the next recursive call consume the current token
        pass

def factor():
    if word.type == 'name':
        w = word
        next_word()
        return ASTNode(
            'Factor',
            [w],
        )
    elif word.type == '(':
        next_word()
        e = expr()
        if word.type != ')':
            raise InvalidSyntax('Expected ), found', word.type)
        else:
            next_word()
            return ASTNode(
                'Factor',
                ['(', e, ')'],
            )
    else:
        raise InvalidSyntax('Unexpected: ', word.type)

def pprint(node, indent=0):
    print('{}{}'.format('\t'*indent, node))
    if isinstance(node, ASTNode):
        for child in node.children:
            pprint(child, indent+1)

word = None
words = None

def main():
    prog = 'a * (b + c)'
    lexemes = scan(prog)
    print(lexemes)

    global words
    words = iter(lexemes)
    next_word()
    e = expr()
    pprint(e)
    #import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    main()

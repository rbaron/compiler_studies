"""Variation of the example_scanner.py with a few enhancements.

"""

KEYWORDS = {
    'if',
    'else',
    'double',
    'char',
    'int',
    'long',
    'signed',
    'struct',
    'typedef',
    'unsigned',
    'void',
}


class MalformedInput(Exception):
    pass


class Lexeme:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return '<Lexeme {} {}>'.format(self.type, self.value)

    def __str__(self):
        return self.__repr__()


def is_number(token):
    return token >= '0' and token <= '9'

def is_whitespace(token):
    return token in ' \n\t'

def is_start_of_name(token):
    return token >= 'a' and token <= 'z'

def is_start_of_multiline_comment(token, next):
    return token == '/' and next == '*'

def is_start_of_single_line_comment(token, next):
    return token == '/' and next == '/'

def is_alphanumeric(token):
    return is_number(token) or is_start_of_name(token) or token in '_'

def is_operator(token):
    return token in '=-+/*><|^&~'


def scanner(type, terminator=None):
    def decorator(predicate):
        def inner(program, pos):
            end_pos = pos
            while end_pos < len(program) and predicate(program[end_pos]):
                end_pos += 1

                if terminator is not None and terminator(program[end_pos-1]):
                    break

            if type == 'operator':
                return end_pos, Lexeme(program[pos:end_pos], program[pos:end_pos])
            else:
                return end_pos, Lexeme(type, program[pos:end_pos])
        return inner
    return decorator


def guarded_scanner(type, start_guard, end_guard):
    def decorator(f):
        def inner(program, pos):
            end_pos = pos

            if program[end_pos:end_pos+len(start_guard)] != start_guard:
                raise MalformedInput('Malformed as pos {}. Expected {}, found {}'.format(
                    pos, start_guard, program[end_pos:end_pos+len(start_guard)]))

            end_pos += len(start_guard)

            while True:
                if program[end_pos:end_pos+len(end_guard)] != end_guard:
                    end_pos += 1

                else:
                    end_pos += len(end_guard)
                    break

            return end_pos, Lexeme(type, program[pos:end_pos])
        return inner
    return decorator


@guarded_scanner('string', '"', '"')
def scan_double_quote_string():
    pass

@guarded_scanner('string', '\'', '\'')
def scan_single_quote_string():
    pass

@guarded_scanner('comment', '/*', '*/')
def scan_multiline_comment():
    pass

def scan_single_line_comment(program, pos):
    @guarded_scanner('comment', '//', '\n')
    def inner():
        pass

    end_pos, lexeme = inner(program, pos)
    return end_pos, Lexeme(lexeme.type, lexeme.value[:-1])

@scanner('num')
def scan_number(token):
    return is_number(token)

@scanner('whitespace')
def scan_whitespace(token):
    return is_whitespace(token)

@scanner('name')
def scan_name(token):
    return is_alphanumeric(token)

@scanner('operator')
def scan_operator(token):
    return is_operator(token)


def scan(program):

    lexemes = []

    pos = 0
    while pos < len(program):
        token = program[pos]

        if is_number(token):
            pos, lexeme = scan_number(program, pos)
            lexemes.append(lexeme)

        elif is_whitespace(token):
            pos, _ = scan_whitespace(program, pos)

        elif pos + 1 < len(program) and is_start_of_multiline_comment(token, program[pos+1]):
            pos, lexeme = scan_multiline_comment(program, pos)
            lexemes.append(lexeme)

        elif pos + 1 < len(program) and is_start_of_single_line_comment(token, program[pos+1]):
            pos, lexeme = scan_single_line_comment(program, pos)
            lexemes.append(lexeme)

        elif is_operator(token):
            pos, lexeme = scan_operator(program, pos)
            lexemes.append(lexeme)

        elif token in '=,(){}[]':
            pos += 1
            lexemes.append(Lexeme(token, program[pos-1]))

        elif token == '"':
            pos, lexeme = scan_double_quote_string(program, pos)
            lexemes.append(lexeme)

        elif token == '\'':
            pos, lexeme = scan_single_quote_string(program, pos)
            lexemes.append(lexeme)

        elif is_start_of_name(token):
            pos, lexeme = scan_name(program, pos)

            if lexeme.value in KEYWORDS:
                lexeme.type = 'keyword'

            lexemes.append(lexeme)

        else:
            raise MalformedInput('Invalid token: {}'.format(token))

    return lexemes


if __name__ == '__main__':
    program = """
    int my_n = 5/2;

    // this is a single line comment

    /* this is a
    multi
    line
    comment */

    void my_func(int a, char *b) { print("hello"); };

    """

    for lexeme in scan(program):
        print(lexeme)

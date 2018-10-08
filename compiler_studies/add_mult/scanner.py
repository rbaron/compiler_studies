import enum


class Lexeme:
    def __init__(self, type, value):
        self.type = type
        self.value = value


def is_number(token):
    return token >= '0' and token <= '9'


def is_identifier(token):
    return token >= 'a' and token <= 'z'


def is_whitespace(token):
    return token in ' \r\n\t'


def is_operator(token):
    return token in '+*'


def is_paren(token):
    return token in '()'


def scan_number(string, pos):
    end_pos = pos
    while end_pos < len(string) and is_number(string[end_pos]):
        end_pos += 1
    return end_pos, Lexeme('number', string[pos:end_pos])


def scan_identifier(string, pos):
    end_pos = pos
    while end_pos < len(string) and is_identifier(string[end_pos]):
        end_pos += 1
    return end_pos, Lexeme('identifier', string[pos:end_pos])


def scan_operator(string, pos):
    return pos + 1, Lexeme('operator', string[pos])


def scan(string):
    lexemes = []

    pos = 0
    while pos < len(string):
        token = string[pos]

        if is_number(token):
            pos, lexeme = scan_number(string, pos)
            lexemes.append(lexeme)

        elif is_identifier(token):
            pos, lexeme = scan_identifier(string, pos)
            lexemes.append(lexeme)

        elif is_operator(token):
            pos, lexeme = scan_operator(string, pos)
            lexemes.append(lexeme)

        elif is_whitespace(token):
            pos += 1

        elif is_paren(token):
            lexemes.append(Lexeme('paren', token))
            pos += 1

        else:
            raise ValueError('Unrecognized token: {}'.format(token))

    return lexemes


def test():
    source = 'a + 1 * c'
    res = scan(source)
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    test()

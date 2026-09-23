"""
lexer.py — Tokenizer for Pebble (BYOL Week 1 deliverable)

Converts raw Pebble source text into a flat list of Token objects.
See spec.md for the full grammar and token table.

Unlike a brace-and-semicolon language, Pebble statements end at a
newline and blocks are closed with an explicit `end` keyword, so the
lexer emits NEWLINE tokens as real, significant tokens (consecutive
blank lines collapse into a single one).
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

KEYWORDS = {"set", "to", "tell", "when", "then", "otherwise", "end"}

# Multi-character operators must be checked before their single-char prefix.
TWO_CHAR_OPS = {
    "<>": "NEQ",
    "<=": "LTE",
    ">=": "GTE",
}

ONE_CHAR_OPS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "&": "AMP",
    "=": "EQ",
    "<": "LT",
    ">": "GT",
}

PUNCTUATION = {
    "(": "LPAREN",
    ")": "RPAREN",
}


@dataclass
class Token:
    type: str       # e.g. "INT", "IDENT", "SET", "NEWLINE", "EOF" ...
    value: str      # the literal text
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, {self.line}:{self.column})"


class LexError(Exception):
    """Raised when the lexer meets a character or construct it can't tokenize."""

    def __init__(self, message, line, column):
        super().__init__(f"LexError at {line}:{column}: {message}")
        self.line = line
        self.column = column


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    # -- low-level helpers ---------------------------------------------

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < self.length else ""

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _at_end(self) -> bool:
        return self.pos >= self.length

    # -- skipping (newlines are NOT skipped here — they're significant) --

    def _skip_spaces_and_comments(self):
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
            elif ch == "-" and self._peek(1) == "-":
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            else:
                break

    # -- token producers ----------------------------------------------

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        digits = []
        while not self._at_end() and self._peek().isdigit():
            digits.append(self._advance())
        return Token("INT", "".join(digits), start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        chars = []
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        text = "".join(chars)
        token_type = text.upper() if text in KEYWORDS else "IDENT"
        return Token(token_type, text, start_line, start_col)

    def _read_string(self) -> Token:
        start_line, start_col = self.line, self.column
        self._advance()  # consume opening quote
        chars = []
        while True:
            if self._at_end():
                raise LexError("unterminated string literal", start_line, start_col)
            ch = self._peek()
            if ch == '"':
                self._advance()  # consume closing quote
                break
            if ch == "\n":
                raise LexError("unterminated string literal (newline in string)",
                                start_line, start_col)
            if ch == "\\":
                self._advance()
                esc = self._peek()
                mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                if esc not in mapping:
                    raise LexError(f"unknown escape sequence '\\{esc}'",
                                    self.line, self.column)
                chars.append(mapping[esc])
                self._advance()
            else:
                chars.append(self._advance())
        return Token("STRING", "".join(chars), start_line, start_col)

    def _read_operator_or_punct(self) -> Token:
        start_line, start_col = self.line, self.column
        two = self._peek() + self._peek(1)
        if two in TWO_CHAR_OPS:
            self._advance()
            self._advance()
            return Token(TWO_CHAR_OPS[two], two, start_line, start_col)

        one = self._peek()
        if one in ONE_CHAR_OPS:
            self._advance()
            return Token(ONE_CHAR_OPS[one], one, start_line, start_col)
        if one in PUNCTUATION:
            self._advance()
            return Token(PUNCTUATION[one], one, start_line, start_col)

        raise LexError(f"illegal character {one!r}", start_line, start_col)

    # -- main entry point ------------------------------------------------

    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            self._skip_spaces_and_comments()

            if self._at_end():
                if tokens and tokens[-1].type != "NEWLINE":
                    tokens.append(Token("NEWLINE", "", self.line, self.column))
                tokens.append(Token("EOF", "", self.line, self.column))
                break

            ch = self._peek()

            if ch == "\n":
                start_line, start_col = self.line, self.column
                # Collapse this and any further blank lines into one NEWLINE.
                while not self._at_end() and self._peek() == "\n":
                    self._advance()
                    self._skip_spaces_and_comments()
                if tokens and tokens[-1].type != "NEWLINE":
                    tokens.append(Token("NEWLINE", "\\n", start_line, start_col))
                continue

            if ch.isdigit():
                tokens.append(self._read_number())
            elif ch.isalpha() or ch == "_":
                tokens.append(self._read_identifier())
            elif ch == '"':
                tokens.append(self._read_string())
            else:
                tokens.append(self._read_operator_or_punct())

        return tokens


def tokenize(source: str) -> list[Token]:
    """Convenience wrapper: tokenize a source string in one call."""
    return Lexer(source).tokenize()


# ---------------------------------------------------------------------------
# Manual smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = '''
    set x to 5
    set y to 10
    set z to x + y * 2   -- arithmetic
    tell z

    set name to "Kelvin"
    tell "Hello, " & name

    when z >= 20 then
        tell "big"
    otherwise
        tell "small"
    end
    '''

    for tok in tokenize(sample):
        print(tok)

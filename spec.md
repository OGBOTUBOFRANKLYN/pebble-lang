# Pebble — Language Specification

**Course:** CSC 404 — Survey of Programming Languages (NDU)
**Project:** Build Your Own Language (BYOL)
**Milestone:** Week 1 — Language Specification & Lexical Analysis

## 1. Overview

Pebble is a small, Turing-incomplete toy language for arithmetic and simple
conditional logic. It supports:

- Variable declaration and assignment (`set ... to ...`)
- Integer arithmetic with standard operator precedence
- String values and concatenation (`&`)
- Output via `tell`
- A single, non-chained conditional (`when / then / otherwise / end`)

It has **no loops, no functions, and no recursion** — a program's
statements run top to bottom exactly once. Statements are terminated by a
newline, not a semicolon, and blocks are closed with an explicit `end`
keyword rather than braces.

## 2. Example Snippets

**2.1 — Arithmetic and variables**
```pebble
set x to 5
set y to 10
set z to x + y * 2
tell z
```

**2.2 — Strings and concatenation**
```pebble
set name to "Kelvin"
tell "Hello, " & name
```

**2.3 — Conditional**
```pebble
set score to 72
when score >= 50 then
    tell "Pass"
otherwise
    tell "Fail"
end
```

**2.4 — Grouping and precedence**
```pebble
set a to 3
set b to 4
set c to (a + b) * (a - b)
tell c
```

**2.5 — Combined output with a comment**
```pebble
-- compute and report a total
set total to 42
tell "Total: "
tell total
```

## 3. Tokens

| Token       | Description                                  | Examples              |
|-------------|-----------------------------------------------|------------------------|
| `IDENT`     | Identifier: letter, then letters/digits/`_`   | `x`, `score`, `my_var` |
| `INT`       | Integer literal                               | `0`, `42`, `1000`      |
| `STRING`    | Text in double quotes                         | `"hello"`              |
| `NEWLINE`   | Statement terminator                          | end of physical line   |
| Keywords    | `set`, `to`, `tell`, `when`, `then`, `otherwise`, `end` | —              |
| Operators   | `+ - * / & = <> < > <= >=`                    | —                       |
| Punctuation | `( )`                                          | —                       |

Comments run from `--` to end of line. Consecutive blank lines collapse
into a single `NEWLINE` token, so blank lines between statements are
allowed and ignored. Any character not covered above is illegal and must
be rejected with a lexer error rather than crashing.

## 4. Formal Grammar (EBNF)

```ebnf
program      = { statement } ;

statement    = set_stmt
             | tell_stmt
             | when_stmt ;

set_stmt     = "set" , identifier , "to" , expression , NEWLINE ;

tell_stmt    = "tell" , expression , NEWLINE ;

when_stmt    = "when" , expression , "then" , NEWLINE ,
               { statement } ,
               [ "otherwise" , NEWLINE , { statement } ] ,
               "end" , NEWLINE ;

expression   = comparison ;

comparison   = term , { comp_op , term } ;

comp_op      = "=" | "<>" | "<" | ">" | "<=" | ">=" ;

term         = factor , { ( "+" | "-" | "&" ) , factor } ;

factor       = unary , { ( "*" | "/" ) , unary } ;

unary        = [ "-" ] , primary ;

primary      = INT
             | STRING
             | identifier
             | "(" , expression , ")" ;

identifier   = letter , { letter | digit | "_" } ;

INT          = digit , { digit } ;

STRING       = '"' , { character } , '"' ;

letter       = "a".."z" | "A".."Z" ;
digit        = "0".."9" ;
```

## 5. Semantics Notes

- `set NAME to EXPR` both declares and assigns; re-declaring a name
  rebinds it in the same environment (one flat symbol table, no block
  scoping).
- `&` is the dedicated concatenation operator — it always produces a
  string, converting a non-string operand to its string form. Arithmetic
  `+` is reserved for numbers only, so `1 + 2` and `"a" & "b"` are each
  unambiguous by which operator is used.
- `=` means equality (not assignment — assignment is the `set ... to`
  keyword form, so `=` never needs to do double duty). `<>` is
  not-equal.
- `when` supports **at most one** `otherwise` — there is no `elif`-style
  chaining.
- Precedence, high to low: `* /` → `+ - &` → comparisons
  (`= <> < > <= >=`). Parentheses override precedence.
- No loops, no function definitions or calls — every Pebble program halts
  after its statements run once, which is what keeps it Turing-incomplete.

# Pebble

A small, Turing-incomplete toy programming language and interpreter, built
from scratch in Python for **CSC 404 — Survey of Programming Languages**
(Niger Delta University), as the term's **Build Your Own Language (BYOL)**
project.

Pebble supports variables, integer arithmetic with standard operator
precedence, strings with dedicated concatenation, output via `tell`, and a
single (non-chained) `when` / `otherwise` conditional. It has no loops,
functions, or recursion. Statements end at a newline rather than a
semicolon, and blocks close with an explicit `end` keyword rather than
braces — see [`spec.md`](spec.md) for the full specification and grammar.

## Project Status

| Milestone | Deliverable(s)              | Status         |
|-----------|------------------------------|----------------|
| Week 1    | `spec.md`, `lexer.py`        | ✅ Done         |
| Week 2    | `parser.py`                  | ⬜ Not started  |
| Week 3    | `evaluator.py`, `main.py`, `.pebble` test script | ⬜ Not started |

## Example

```pebble
set score to 72
when score >= 50 then
    tell "Pass"
otherwise
    tell "Fail"
end
```

## Running the lexer

```bash
python3 lexer.py
```

Runs the lexer against a built-in sample program and prints the resulting
token stream.

## Author

Ogbotobo Philip Franklyn UG/22/5850

# rewrite-python

This repository is a work-in-progress implementation of Rewrite Python language support.

## Implementation Progress

This is largely based on the [Python grammar specification](https://docs.python.org/3/reference/grammar.html).

## Parser Development and Testing

The Python parser is being implemented in Python, but its printer is implemented in Java. So regardless of whether the tests are written in Java or in Python, both a Python and a Java process are required to validate the parser's results.
As we already have plenty of tests written in Java, this section describes how to run these and also debug the parser.
Thus, the idea is to run OpenRewrite JUnit tests, which behind the scenes parse the Python sources using a Python application, where the two applications communicate via TCP sockets (using the LST remoting protocol).
In the setup described here it is at the time of writing important that the GitHub repos are cloned in a organization/repo structure.

1. Clone both `moderneinc/rewrite-remote` and `openrewrite/rewrite-python` (here we are assuming `~/git` to be the parent directory)
   ```shell
   mkdir -p ~/git/moderneinc && gh repo clone moderneinc/rewrite-remote ~/git/moderneinc/rewrite-remote
   mkdir -p ~/git/openrewrite && gh repo clone openrewrite/rewrite-python ~/git/openrewrite/rewrite-python
   ```
2. Make sure Python 3.8 and Poetry are installed
   ```shell
   brew install python@3.8
   brew install poetry
   ```
3. Create a Python virtual environment (here we are going to use `~/.venv` but any directory works) and activate it
   ```shell
   python3.8 -m venv ~/.venv
   source ~/.venv/bin/activate
   ```
4. Switch to `moderneinc/rewrite-remote` and install all dependencies using Poetry
   ```shell
   cd ~/git/moderneinc/rewrite-remote
   poetry install
   ```
5. Open `~/git/openrewrite/rewrite-python/rewrite` in IDEA (or PyCharm)
   ```shell
   idea ~/git/openrewrite/rewrite-python/rewrite
   ```
6. Make sure that the Python plugin is installed and also that the interpreter from the created venv is configured and used
7. Create a new run configuration which runs the Python module `rewrite.remote.server` (typically in debug mode)
8. Now open `~/git/openrewrite/rewrite-python` in a second IDEA workspace and run the JUnit tests from there

### Resources

- [Python Builtins](https://docs.python.org/3/library/functions.html), which are sometimes used to desugar syntax.
- [Python Magic Methods (aka "dunders")](https://docs.python.org/3/library/operator.html), also used for desugaring.

### Statements

| Element                 | Status | Example                           | Mapping Notes                                                                       | Limitations                                       |
|-------------------------|:------:|-----------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------|
| File                    |   ✅    |                                   |                                                                                     |                                                   |
| Simple Statement List   |   ✅    | <pre>a = 1; b=a*2; print(b)</pre> |                                                                                     |                                                   |
| Function Definition     |   ✅    |                                   |                                                                                     |                                                   |
| If Statement            |   ✅    |                                   |                                                                                     |                                                   |
| Class Definition        |   ✅    |                                   | Implemented as `J.ClassDeclaration`. Base classes are stored in `implementings`.    |                                                   |
| With Statement          |   ✅    |                                   | Implemented as `J.Try` with a non-empty resources list.                             |                                                   |
| For Statement           |   ✅    |                                   |                                                                                     |                                                   |
| Try Statement           |   ✅    |                                   |                                                                                     |                                                   |
| While Statement         |   ✅    |                                   |                                                                                     |                                                   |
| Match Statement         |   ✅    |                                   |                                                                                     |                                                   |
| Except Statement        |   ✅    |                                   |                                                                                     |                                                   |
| Assignment Statement    |   ✅    |                                   |                                                                                     |                                                   |
| Augment-Assignment      |   ✅    |                                   | Unsupported: `//`, `**`, `%`, `@`.                                                  |                                                   |
| Return Statement        |   ✅    | <pre>return x</pre>               |                                                                                     |                                                   |
| Import Statement        |   ✅    | <pre>from . import foo</pre>      | Implemented as `J.Import`, with `GroupedStatement` markers.                         |                                                   |
| Raise Statement         |   ✅    |                                   |                                                                                     |                                                   |
| Pass Statement          |   ✅    | <pre>pass</pre>                   | Implemented as `Py.PassStatement`.                                                  |                                                   |
| Delete Statement        |   ✅    | <pre>del x, y</pre>               | Implemented as `Py.DelStatement`.                                                   |                                                   |
| Yield Statement         |   ✅    |                                   |                                                                                     |                                                   |
| Assert Statement        |   ✅    | <pre>assert x, y</pre>            | Implemented as `Py.Assert`.                                                         |                                                   |
| Break Statement         |   ✅    | <pre>break</pre>                  |                                                                                     |                                                   |
| Continue Statement      |   ✅    | <pre>continue</pre>               |                                                                                     |                                                   |
| Global Statement        |   ✅    | <pre>global x</pre>               | Implemented as `Py.VariableScopeStatement`.                                         |                                                   |
| Nonlocal Statement      |   ✅    | <pre>nonlocal x</pre>             | Implemented as `Py.VariableScopeStatement`.                                         |                                                   |
| Decorators              |   ✅    |                                   | Implemented as `J.Annotation`.                                                      | Does not support arbitrary expressions (PEP 614). |
| Type Comments           |   ✅    |                                   |                                                                                     |                                                   |
| Numeric Literal         |   ✅    |                                   |                                                                                     |                                                   |
| String Literal          |   ✅    |                                   |                                                                                     |                                                   |
| Boolean Literal         |   ✅    |                                   |                                                                                     |                                                   |
| None Literal            |   ✅    | <pre>None</pre>                   | Implemented as Java `null`.                                                         |                                                   |
| List Literal            |   ✅    | <pre>[1, 2, 3]</pre>              | Implemented as `__builtins__.list` call.                                            |                                                   |
| Set Literal             |   ✅    | <pre>{1, 2, 3}</pre>              | Implemented as `__builtins__.set` call.                                             |                                                   |
| Dict Literal            |   ✅    | <pre>{1: 2, 3: 4}</pre>           |                                                                                     |                                                   |
| Tuple Literal           |   ✅    | <pre>(1, 2, 3)</pre>              | Implemented as `__builtins__.tuple` call.                                           |                                                   |
| List Comprehension      |   ✅    | <pre>[x for x in xs]</pre>        |                                                                                     |                                                   |
| Set Comprehension       |   ✅    | <pre>{x for x in xs}</pre>        |                                                                                     |                                                   |
| Dict Comprehension      |   ✅    | <pre>{x:x for x in xs}</pre>      |                                                                                     |                                                   |
| Generator Comprehension |   ✅    | <pre>(x for x in xs)</pre>        |                                                                                     |                                                   |
| Yield Expression        |   ✅    | <pre>yield from x</pre>           | Implemented as `Py.YieldExpression`.                                                |                                                   |
| Await Expression        |   ✅    | <pre>await x</pre>                | Implemented as `Py.AwaitExpression`.                                                |                                                   |
| Bitwise Operators       |   ✅    |                                   |                                                                                     |                                                   |
| Arithmetic Operators    |   ✅    |                                   |                                                                                     |                                                   |
| Comparison Operators    |   ✅    |                                   | Non-Java comparisons are implemented using desugared magic methods (e.g. `__eq__`). |                                                   |
| Slices                  |   ✅    |                                   | Implemented using a desugared call to `__builtins__.slice`.                         |                                                   |
| Lambda Expressions      |   ✅    |                                   |                                                                                     |                                                   |
| Call Expressions        |   ✅    | <pre>print(42)</pre>              | Invocation of arbitrary expressions is implemented using desugared `__call__`.      |                                                   |
| Attribute Access        |   ✅    |                                   | Implemented as `J.FieldAccess`.                                                     |                                                   |
| Comments                |   ✅    |                                   | Implemented as `PyComment`.                                                         |                                                   |

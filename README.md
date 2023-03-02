# rewrite-python

This repository is a work-in-progress implementation of Rewrite Python language support.

## Implementation Progress

This is largely based on the [Python grammar specification](https://docs.python.org/3/reference/grammar.html).

### Resources

- [Python Builtins](https://docs.python.org/3/library/functions.html), which are sometimes used to desugar syntax.
- [Python Magic Methods (aka "dunders")](https://docs.python.org/3/library/operator.html), also used for desugaring. 

### Statements

| Element                 | Status | Example                           | Mapping Notes                                                                       | Limitations                                       |
|-------------------------|:------:|-----------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------|
| File                    |   ✅    |                                   |                                                                                     |                                                   |
| Simple Statement List   |   ❌    | <pre>a = 1; b=a*2; print(b)</pre> |                                                                                     |                                                   |
| Function Definition     |   ✅    |                                   |                                                                                     |                                                   |
| If Statement            |   ✅    |                                   |                                                                                     |                                                   |
| Class Definition        |   ✅    |                                   | Implemented as `J.ClassDeclaration`. Base classes are stored in `implementings`.    |                                                   |
| With Statement          |   ❌    |                                   |                                                                                     |                                                   |
| For Statement           |   ✅    |                                   |                                                                                     |                                                   |
| Try Statement           |   ❌    |                                   |                                                                                     |                                                   |
| While Statement         |   ✅    |                                   |                                                                                     |                                                   |
| Match Statement         |   ❌    |                                   |                                                                                     |                                                   |
| Except Statement        |   ❌    |                                   |                                                                                     |                                                   |
| Assignment Statement    |   ✅    |                                   |                                                                                     |                                                   |
| Return Statement        |   ✅    | <pre>return x</pre>               |                                                                                     |                                                   |
| Import Statement        |   ⚠️   | <pre>from . import foo</pre>      | Implemented as `J.Import`.                                                          | No support for multiple imports in one statement. |
| Raise Statement         |   ❌    |                                   |                                                                                     |                                                   |
| Pass Statement          |   ✅    | <pre>pass</pre>                   | Implemented as `Py.PassStatement`.                                                  |                                                   |
| Delete Statement        |   ✅    | <pre>del x, y</pre>               | Implemented as `Py.DelStatement`.                                                   |                                                   |
| Yield Statement         |   ❌    |                                   |                                                                                     |                                                   |
| Assert Statement        |   ✅    | <pre>assert x, y</pre>            | Implemented as `Py.Assert`.                                                         |                                                   |
| Break Statement         |   ✅    | <pre>break</pre>                  |                                                                                     |                                                   |
| Continue Statement      |   ✅    | <pre>continue</pre>               |                                                                                     |                                                   |
| Global Statement        |   ❌    | <pre>global x</pre>               |                                                                                     |                                                   |
| Nonlocal Statement      |   ❌    | <pre>nonlocal x</pre>             |                                                                                     |                                                   |
| Decorators              |   ✅    |                                   | Implemented as `J.Annotation`.                                                      | Does not support arbitrary expressions (PEP 614). |
| Type Comments           |   ❌    |                                   |                                                                                     |                                                   |
| Numeric Literal         |   ✅    |                                   |                                                                                     |                                                   |
| String Literal          |   ✅    |                                   |                                                                                     |                                                   |
| Boolean Literal         |   ✅    |                                   |                                                                                     |                                                   |
| None Literal            |   ✅    | <pre>None</pre>                   | Implemented as Java `null`.                                                         |                                                   |
| List Literal            |   ✅    | <pre>[1, 2, 3]</pre>              | Implemented as `__builtins__.list` call.                                            |                                                   |
| Set Literal             |   ✅    | <pre>{1, 2, 3}</pre>              | Implemented as `__builtins__.set` call.                                             |                                                   |
| Dict Literal            |   ✅    | <pre>{1: 2, 3: 4}</pre>           |                                                                                     | Padding of empty dict literals is broken.         |
| Tuple Literal           |   ✅    | <pre>(1, 2, 3)</pre>              | Implemented as `__builtins__.tuple` call.                                           |                                                   |
| List Comprehension      |   ✅    | <pre>[x for x in xs]</pre>        |                                                                                     |                                                   |
| Set Comprehension       |   ✅    | <pre>{x for x in xs}</pre>        |                                                                                     |                                                   |
| Dict Comprehension      |   ✅    | <pre>{x:x for x in xs}</pre>      |                                                                                     |                                                   |
| Generator Comprehension |   ✅    | <pre>(x for x in xs)</pre>        |                                                                                     |                                                   |
| Yield Expression        |   ✅    | <pre>yield from x</pre>           | Implemented as `Py.YieldExpression`.                                                |                                                   |
| Await Expression        |   ✅    | <pre>await x</pre>                | Implemented as `Py.AwaitExpression`.                                                |                                                   |
| Bitwise Operators       |   ❌    |                                   |                                                                                     |                                                   |
| Arithmetic Operators    |   ✅    |                                   |                                                                                     |                                                   |
| Comparison Operators    |   ✅    |                                   | Non-Java comparisons are implemented using desugared magic methods (e.g. `__eq__`). |                                                   |
| Slices                  |   ✅    |                                   | Implemented using a desugared call to `__builtins__.slice`.                         |                                                   |
| Lambda Expressions      |   ❌    |                                   |                                                                                     |                                                   |
| Call Expressions        |   ✅    | <pre>print(42)</pre>              | Invocation of arbitrary expressions is implemented using desugared `__call__`.      |                                                   |
| Attribute Access        |   ✅    |                                   | Implemented as `J.FieldAccess`.                                                     |                                                   |
| Comments                |   ✅    |                                   | Implemented as `PyComment`.                                                         |                                                   |

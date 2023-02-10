## rewrite-python

This repository is a work-in-progress implementation of Rewrite Python language support.

### Project Notes

**2023-02-10 (Gary Olsen)**

- This current goal is to use Python implemtation to help understand non-JVM language implementation issues more generally, rather than to quickly have broad Python language support.
  - Initially we're making no attempt to support Python type inference.
- The current approach is to re-use the Java implementation to the greatest extent possible.
- Known parsing limitations should be documented by test cases using `assertThrows`, with a comment describing the failure conditions.
- The IntelliJ Python plugin is a dependency, and we haven't decided how to include it long-term.
  - For the time being, it's pinned in `#feat-python` on the company Slack (this includes the JAR as well as instructions for how to export it yourself).
  - As I discover unmet runtime dependencies I am accumulating them locally under `lib`, which isn't the best idea but it works for now. I'll add those dependencies to the Gradle build when we make a decision on how to handle the IntelliJ plugin.
- There is no coherent error reporting strategy in the `PythonParser` for now, and the parsing (and testing code) generate a lot of logspew.
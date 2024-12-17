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
2. Make sure Python 3.12 and Uv are installed
   ```shell
   brew install uv
   uv install python
   ```
3. Create a Python virtual environment (here we are going to use `~/.venv` but any directory works) and activate it
   ```shell
   un sync --all-extras
   source ~/.venv/bin/activate
   ```
4. Switch to `moderneinc/rewrite-remote/python` and install all dependencies using Uv
   ```shell
   cd ~/git/moderneinc/rewrite-remote/python/rewrite-remote-test
   uv build
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

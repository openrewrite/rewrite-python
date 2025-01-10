<p align="center">
  <a href="https://docs.openrewrite.org/">
      <img src="https://github.com/openrewrite/rewrite/raw/main/doc/logo-oss.png" alt="OpenRewrite">
    </a>
</p>

<div align="center">
  <h1>rewrite-python</h1>
</div>

<div align="center">

<!-- Keep the gap above this line, otherwise they won't render correctly! -->
[![ci](https://github.com/openrewrite/rewrite-python/actions/workflows/ci.yml/badge.svg)](https://github.com/openrewrite/rewrite-python/actions/workflows/ci.yml)
[![Maven Central](https://img.shields.io/maven-central/v/org.openrewrite/rewrite-python.svg)](https://mvnrepository.com/artifact/org.openrewrite/rewrite-python)
[![Revved up by Gradle Enterprise](https://img.shields.io/badge/Revved%20up%20by-Gradle%20Enterprise-06A0CE?logo=Gradle&labelColor=02303A)](https://ge.openrewrite.org/scans)
[![Contributing Guide](https://img.shields.io/badge/Contributing-Guide-informational)](https://github.com/openrewrite/.github/blob/main/CONTRIBUTING.md)
</div>

## Introduction

This repository is a work-in-progress implementation of OpenRewrite Python language support.

**Note**: For now, this language and the associated recipes are only supported via the [Moderne CLI](https://docs.moderne.io/user-documentation/moderne-cli/getting-started/cli-intro) or the [Moderne Platform](https://docs.moderne.io/user-documentation/moderne-platform/getting-started/running-your-first-recipe) (at least until native build tool support catches up). That being said, the Moderne CLI is free to use for open-source repositories. If your repository is closed-source, though, you will need to obtain a license to use the CLI or the Moderne Platform. [Please contact Moderne to learn more](https://www.moderne.ai/contact-us).

## Getting started

For help getting started with the Moderne CLI, check out our [getting started guide](https://docs.moderne.io/user-documentation/moderne-cli/getting-started/cli-intro). Or, if you'd like to try running these recipes in the Moderne Platform, check out the [Moderne Platform quickstart guide](https://docs.moderne.io/user-documentation/moderne-platform/getting-started/running-your-first-recipe).

## Contributing

We appreciate all types of contributions. See the [contributing guide](https://github.com/openrewrite/.github/blob/main/CONTRIBUTING.md) for detailed instructions on how to get started.

## Development information

### Implementation progress

This is largely based on the [Python grammar specification](https://docs.python.org/3/reference/grammar.html).

### Parser development and testing

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
   uv python install
   ```
3. Create a Python virtual environment and activate it
   ```shell
   cd ~/git/openrewrite/rewrite-python/rewrite
   uv sync --all-extras
   source ./.venv/bin/activate
   ```
4. Switch to `moderneinc/rewrite-remote/python` and install all dependencies using Uv
   ```shell
   cd ~/git/moderneinc/rewrite-remote/python/rewrite-remote
   uv build
   ```
5. Open `~/git/openrewrite/rewrite-python/rewrite` in IDEA (or PyCharm)
   ```shell
   idea ~/git/openrewrite/rewrite-python/rewrite
   ```
6. Make sure that the Python plugin is installed and also that the interpreter from the created venv is configured and used
7. Create a new run configuration which runs the Python module `rewrite_remote.server` (typically in debug mode)
8. Now open `~/git/openrewrite/rewrite-python` in a second IDEA workspace and run the JUnit tests from there

### Resources

- [Python Builtins](https://docs.python.org/3/library/functions.html), which are sometimes used to desugar syntax.
- [Python Magic Methods (aka "dunders")](https://docs.python.org/3/library/operator.html), also used for desugaring.

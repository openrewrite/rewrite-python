# `python-plugin.jar` built from IntelliJ-Community version
Release tag `231.6890`

# IntelliJ Python Plugin Integration

To parse Python files, we use an implementation from the open-source IntelliJ Community project.

## Configuring what's included

In this directory, you'll find the following files:

- `python_plugin.xml` is an IDEA artifact configuration that covers all potential dependencies, but which builds a bloated JAR
  - If you need to change which project modules are included in the bloated JAR, edit them here.
- `build-intellij-dependency.sh` exports a slimmed-down version of the plugin JAR based on what Python parsing actually requires.
  - The script runs a Java task that parses a corpus of Python files while collecting classes that are actually loaded.
  - The bloated JAR is temporarily moved into `lib/` so that any dependent class can be accessed.
- `extra_classnames.txt` is a newline-delimited list of additional Java classes that should always be copied from the bloated JAR
- `extra_resources.txt` is a newline-delimited list of additional resources that should be always copied from the bloated JAR  

## Building the slimmed-down IntelliJ Python plugin dependency

1. IntelliJ Setup:
   1. Clone `git@github.com:JetBrains/intellij-community.git` in the same parent directory as the Rewrite clone.
   2. Add a new artifact export to the IntelliJ Community project: 
      ```bash
      cp python_plugin.xml ../intellij-community/.idea/artifacts/python_plugin.xml
      ```
   3. Open the Intellij Community project in IntelliJ IDEA.
   4. Build the bloated JAR via "Build > Build Artifacts ... > python-plugin".
2. Run `python-plugin/build-intellij-dependency.sh`; this will create (or overwrite) `lib/python-plugin.jar`.

## Verifying a plugin JAR

After following the above steps, run the project tests and check that none fail due to classloading errors.

If there are classloading errors:
1. Add the class to `CollectIntelliJDependenciesAsm#run()`.

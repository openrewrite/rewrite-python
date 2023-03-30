#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
BUILD_DIR="$(realpath "$SCRIPT_DIR/build")"
PROJECT_DIR="$(realpath "$SCRIPT_DIR/..")"
PARENT_DIR="$(realpath "$PROJECT_DIR/..")"
GRADLE_CMD="$PROJECT_DIR/gradlew"

#
# Configure where the IntelliJ Community checkout lives.
#

INTELLIJ_DIR="$PARENT_DIR/intellij-community"

FULL_JAR_PATH="$INTELLIJ_DIR/out/artifacts/python_plugin/python-plugin.jar"

#
# This should match where the Gradle project expects JARs to add to its classpath.
#

DEPENDENCY_JAR_PATH="$PROJECT_DIR/lib/python-plugin.jar"

#
#

rm -rf "$BUILD_DIR"
mkdir "$BUILD_DIR"

if [[ ! -d "$INTELLIJ_DIR" ]] ; then
    echo "Expected to find the IntelliJ Community project cloned to $INTELLIJ_DIR but it does not exist."
    exit 1
fi

if [[ ! -f "$FULL_JAR_PATH" ]] ; then
    echo "Expected to find the bloated JAR in $FULL_JAR_PATH but it does not exist."
    echo "Did you run the IntelliJ IDEA Artifact export? (see README.md)"
    exit 1
fi

IDENTIFIED_CLASSNAMES_FILE="$BUILD_DIR/classnames.txt"
EXTRA_CLASSNAMES_FILE="$SCRIPT_DIR/extra_classnames.txt"
EXTRA_RESOURCES_FILE="$SCRIPT_DIR/extra_resources.txt"
REPACKAGE_ITEMS_FILE="$BUILD_DIR/classpath.txt"

echo "Identifying classes used by the IntelliJ plugin's Python parser.."

DEPENDENCY_JAR_BACKUP_PATH="$DEPENDENCY_JAR_PATH.bak"
if [[ -f "$DEPENDENCY_JAR_PATH" ]] ; then
  echo "  Backing up $(basename "$DEPENDENCY_JAR_PATH") to $(basename "$DEPENDENCY_JAR_BACKUP_PATH").."
  mv "$DEPENDENCY_JAR_PATH" "$DEPENDENCY_JAR_BACKUP_PATH"
fi

echo "  Copying the bloated JAR for the Java task.."
cp "$FULL_JAR_PATH" "$DEPENDENCY_JAR_PATH"

echo "  Running the Java task via Gradle.."
$GRADLE_CMD printIntelliJDependencies 2>&1 | \
  grep "^class" | \
  grep "$(basename "$DEPENDENCY_JAR_PATH")" | \
  cut -f2 > "$IDENTIFIED_CLASSNAMES_FILE"
TASK_EXIT_CODE="${PIPESTATUS[0]}"

echo "  Removing the bloated JAR.."
rm "$DEPENDENCY_JAR_PATH"

if [[ -f "$DEPENDENCY_JAR_BACKUP_PATH" ]] ; then
  echo "  Restoring backup from $(basename "$DEPENDENCY_JAR_BACKUP_PATH") to $(basename "$DEPENDENCY_JAR_PATH").."
  mv "$DEPENDENCY_JAR_BACKUP_PATH" "$DEPENDENCY_JAR_PATH"
fi

if [ "$TASK_EXIT_CODE" -ne 0 ]; then
  echo "Java task exited with a non-zero status. Exiting."
  exit "$TASK_EXIT_CODE"
fi

IDENTIFIED_CLASSNAMES_COUNT=$(wc -l < "$IDENTIFIED_CLASSNAMES_FILE" | tr -d ' ')
echo "  Found $IDENTIFIED_CLASSNAMES_COUNT classes."

EXTRA_CLASSNAMES_COUNT=$(wc -l < "$EXTRA_CLASSNAMES_FILE" | tr -d ' ')
EXTRA_RESOURCES_COUNT=$(wc -l < "$EXTRA_RESOURCES_FILE" | tr -d ' ')
echo "Adding $EXTRA_CLASSNAMES_COUNT extra classes and $EXTRA_RESOURCES_COUNT extra resources to the copy list.."

cat "$IDENTIFIED_CLASSNAMES_FILE" "$EXTRA_CLASSNAMES_FILE" |
  sed 's/\./\//g' |
  sed -r 's/(.*)/\1.class/' > "$REPACKAGE_ITEMS_FILE"
cat "$EXTRA_RESOURCES_FILE" >> "$REPACKAGE_ITEMS_FILE"

mkdir "$BUILD_DIR/classes"
REPACKAGE_ITEMS_COUNT=$(wc -l < "$REPACKAGE_ITEMS_FILE" | tr -d ' ')
echo "Extracting $REPACKAGE_ITEMS_COUNT classes and resources from the bloated JAR.."
pushd > /dev/null "$BUILD_DIR/classes" || exit
jar xf "$FULL_JAR_PATH" "@$REPACKAGE_ITEMS_FILE"
popd > /dev/null || exit

echo "Repackaging JAR file.."
BUILD_JAR_PATH="$BUILD_DIR/output.jar"
jar cf "$BUILD_JAR_PATH" -C "$BUILD_DIR/classes" .

cp "$BUILD_JAR_PATH" "$DEPENDENCY_JAR_PATH"
echo "Copied to $DEPENDENCY_JAR_PATH"
#!/bin/bash

# Enable globstar so ** works recursively
shopt -s globstar

# Clean tmp and recompile
rm -rf tmp
mkdir -p tmp

javac -d tmp ../../src/server/engine/**/*.java
javac -d tmp -cp tmp ./**/*.java

failures=0

# Run UtilsTest manually
echo "tests.engine.UtilsTest:"
utils_output=$(java -cp tmp tests.engine.UtilsTest 2>&1)
exit_code=$?
echo "$utils_output"
if [ $exit_code -ne 0 ]; then
    echo "❌ tests.engine.UtilsTest failed"
    failures=$((failures + 1))
else
    echo "✅ tests.engine.UtilsTest passed"
fi
echo

# Group and run T[y]Tests
for group_dir in tmp/tests/engine/algorithms/A*/; do
    group_name=$(basename "$group_dir")
    echo "$group_name:"

    for class_file in "$group_dir"*.class; do
        class_name=$(echo "$class_file" | sed 's|tmp/||; s|/|.|g; s|\.class$||')
        test_short_name=$(basename "$class_file" .class)

        output=$(java -cp tmp "$class_name" 2>&1)
        exit_code=$?

        if [ $exit_code -ne 0 ]; then
            echo "  ❌ $test_short_name failed"
            failures=$((failures + 1))
        else
            echo "  ✅ $test_short_name passed"
        fi

        while IFS= read -r line; do
            echo "    $line"
        done <<< "$output"

        echo
    done
done

# Clean up
rm -r tmp

# Exit code summary
if [ $failures -eq 0 ]; then
    echo "✅ All tests passed"
    exit 0
else
    echo "❌ $failures test(s) failed"
    exit 1
fi
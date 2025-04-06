#!/bin/bash
# Compile sources and test files
javac -d bin ../../src/server/engine/**/*.java
javac -d bin -cp bin ./*.java ./**/*.java

failures=0

# Run UtilsTest manually
echo "tests.engine.UtilsTest:"
java -cp bin tests.engine.UtilsTest
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "❌ tests.engine.UtilsTest failed"
    failures=$((failures + 1))
else
    echo "✅ tests.engine.UtilsTest passed"
fi
echo

# Run all tests under tests.engine.algorithms
for class_file in $(find bin/tests/engine/algorithms -name "*.class"); do
    class_name=$(echo "$class_file" | sed 's|bin/||; s|/|.|g; s|\.class$||')
    echo "$class_name:"
    java -cp bin "$class_name"
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "❌ $class_name failed"
        failures=$((failures + 1))
    else
        echo "✅ $class_name passed"
    fi
    echo
done

# Clean up
rm -r bin

# Exit with 0 if all passed, non-zero if any failed
if [ $failures -eq 0 ]; then
    echo "✅ All tests passed"
    exit 0
else
    echo "❌ $failures test(s) failed"
    exit 1
fi
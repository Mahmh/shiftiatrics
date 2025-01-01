#!/bin/bash
javac -d bin ../../src/server/engine/*.java
javac -d bin -cp bin ./ShiftSchedulerTest.java
java -cp bin tests.engine.ShiftSchedulerTest
rm -r bin
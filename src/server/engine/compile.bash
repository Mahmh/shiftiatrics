#!/bin/bash
cd ../../..
javac -d src/server/engine/tmp src/server/engine/**/*.java src/server/engine/algorithms/**/*.java  src/server/engine/Main.java
jar cfm src/server/engine/engine.jar src/server/engine/MANIFEST.MF -C src/server/engine/tmp server/engine
jar tf src/server/engine/engine.jar
rm -r src/server/engine/tmp
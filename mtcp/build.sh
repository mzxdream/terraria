#!/bin/bash
BUILD_PATH=build
if [ ! -d $BUILD_PATH ]; then
    mkdir -p $BUILD_PATH 1>/dev/null 2>&1 || echo "failed to created dir ${BUILD_PATH}"
fi
cd $BUILD_PATH && cmake -DCMAKE_BUILD_TYPE=Debug ../ && make

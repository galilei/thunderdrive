#!/bin/bash

find . -name *.py -exec autoflake --in-place --remove-unused-variables --remove-all-unused-imports {} \;

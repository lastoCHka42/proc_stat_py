#!/bin/bash

top -b -n 2 -d 0.1 -p $1 | awk 'END{printf "%s", $9}'

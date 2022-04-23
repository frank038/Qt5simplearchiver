#!/bin/bash
thisdir=$(dirname "$0")
cd $thisdir
./qt5archiver.py  "$@" &
cd $HOME

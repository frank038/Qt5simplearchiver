#!/bin/bash
thisdir=$(dirname "$0")
cd $thisdir
python3 qt5archiver.py  "$@" &
cd $HOME

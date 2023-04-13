#!/bin/bash

set -e

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

find $SCRIPTPATH | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

if [ -d $SCRIPTPATH/data/binaries ]; then
  rm -rf $SCRIPTPATH/data/binaries;
fi
if [ -d $SCRIPTPATH/data/preprocessed_sources ]; then
  rm -rf $SCRIPTPATH/data/preprocessed_sources;
fi
if [ -d $SCRIPTPATH/data/fingerprint ]; then
  rm -rf $SCRIPTPATH/data/fingerprint;
fi
if [ -d $SCRIPTPATH/data/sources ]; then
  rm -rf $SCRIPTPATH/data/sources;
fi
if [ -d $SCRIPTPATH/data/classes_summaries ]; then
  rm -rf $SCRIPTPATH/data/classes_summaries;
fi
if [ -d $SCRIPTPATH/data/working_dir ]; then
  rm -rf $SCRIPTPATH/data/working_dir;
fi
if [ -f $SCRIPTPATH/data/github_projects/git_testing_output_simple.csv ]; then
  rm $SCRIPTPATH/data/github_projects/git_testing_output_simple.csv;
fi
if [ -f $SCRIPTPATH/data/github_projects/git_testing_output_simple.csv ]; then
  rm $SCRIPTPATH/data/github_projects/git_testing_output_simple.csv;
fi
if [ -f $SCRIPTPATH/data/github_projects/valid_projects.csv ]; then
  rm $SCRIPTPATH/data/github_projects/valid_projects.csv;
fi
if [ -f $SCRIPTPATH/parsing/classes/cpp_parser.py ]; then
  rm $SCRIPTPATH/parsing/classes/cpp_parser.py;
fi
if [ -d $SCRIPTPATH/data/github_projects/projects ]; then
  rm -rf $SCRIPTPATH/data/github_projects/projects;
fi
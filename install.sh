#!/bin/bash

set -e

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

read_dom () {
    local IFS=\>
    read -d \< ENTITY CONTENT
}

while read_dom; do
    if [[ $ENTITY = "clang_version" ]] ; then
        clang_version=$CONTENT
    fi
done < $SCRIPTPATH/configurations/configurations.xml

beginswith() { case $2 in "$1"*) true;; *) false;; esac; }

found=false
for f in /usr/lib/*; do
  IFS='/' read -r -a splitted_path <<< "$f"
  filename="${splitted_path[3]}"
  if beginswith llvm- "$filename"; then
    IFS='-' read -r -a splitted_filename <<< "$filename"
    version=${splitted_filename[1]}
    re='^[0-9]+$'
    if [[ $version =~ $re ]]; then
      if [[ $clang_version == $version ]]; then
        found=true
        break
      fi
    fi
  fi
done
if [ "$found" == false ]; then
  echo "clang-$clang_version not installed. Please install CLANG with 'sudo apt install clang-$clang_version' or change the clang version from the configuration file." >&2; exit 1
fi
if [ ! -f /usr/lib/llvm-$clang_version/lib/libclang-$clang_version.so ]; then
  sudo ln -s /usr/lib/llvm-$clang_version/lib/libclang-$clang_version.so.1 /usr/lib/llvm-$clang_version/lib/libclang-$clang_version.so
fi
if [ ! -d $SCRIPTPATH/data/binaries ]; then
  mkdir $SCRIPTPATH/data/binaries;
fi
if [ ! -d $SCRIPTPATH/data/preprocessed_sources ]; then
  mkdir $SCRIPTPATH/data/preprocessed_sources;
fi
if [ ! -d $SCRIPTPATH/data/fingerprint ]; then
  mkdir $SCRIPTPATH/data/fingerprint;
fi
if [ ! -d $SCRIPTPATH/data/sources ]; then
  mkdir $SCRIPTPATH/data/sources;
fi
if [ ! -d $SCRIPTPATH/data/classes_summaries ]; then
  mkdir $SCRIPTPATH/data/classes_summaries;
fi
if [ ! -d $SCRIPTPATH/data/working_dir ]; then
  mkdir $SCRIPTPATH/data/working_dir;
fi
if [ ! -d $SCRIPTPATH/data/fingerprints_db ]; then
  mkdir $SCRIPTPATH/data/fingerprints_db;
fi
if [ ! -d $SCRIPTPATH/parsing/classes ]; then
  mkdir $SCRIPTPATH/parsing/classes;
fi
if [ ! -f $SCRIPTPATH/parsing/classes/cpp_parser.py ]; then
  sed "s/__CLANG_VERSION__/$clang_version/g" $SCRIPTPATH/parsing/templates/cpp_parser_template.py > $SCRIPTPATH/parsing/classes/cpp_parser.py
fi

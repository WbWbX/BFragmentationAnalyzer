#!/usr/bin/env bash

if (( $# < 2 )); then
    echo "Run as $0 condor_dir condor.sub"
    exit 1
fi

echo "Creating condor jobs inside of $1"

mkdir -p $1/log
condor_submit DIR=$1 $2

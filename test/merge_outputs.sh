#!/usr/bin/env bash

if (( $# < 1 )); then
    echo "Run as $0 condor_dir"
    exit 1
fi

pushd $1

tags=$(ls -1 xb_*_*_*.root | sed -n 's/xb_\(.*\)_.*_.*\.root/\1/p' | sort | uniq)

for tag in ${tags}; do
    echo $tag
    hadd -f xb_${tag}.root xb_${tag}_*_*.root && rm xb_${tag}_*_*.root
done

popd

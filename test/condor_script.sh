#!/usr/bin/env bash

echo $*

JOBID=$1
OUTDIR=${_CONDOR_JOB_IWD}/$2
CMSDIR=$3
maxEvents=$4
tune=$5
frag=$6
param=$7
tag=$8
seed=$((1000+${JOBID}))

pushd ${CMSDIR}/src
eval `scramv1 runtime -sh`
popd

outFile=xb_${tag}_${JOBID}.root
echo ${outFile}
cmsRun ${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/test/runBFragmentationAnalyzer_cfg.py maxEvents=$maxEvents frag=$frag param=$param tune=$tune outputFile=${outFile} seed=${seed}

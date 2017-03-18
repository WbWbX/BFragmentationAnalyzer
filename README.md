# Introduction

# Installation
This module depends on the pseudo-top producer and is expected to run for CMSSW versions >80x.
```
cmsrel CMSSW_8_0_26_patch1
cd CMSSW_8_0_26_patch1/src 
cmsenv
git cms-merge-topic -u intrepid42:pseudotoprivet_80x
cd TopQuarkAnalysis
git clone ssh://git@gitlab.cern.ch:7999/CMS-TOPPAG/BFragmentationAnalyzer.git
cd -
scram b
```

# Description 
Two plugins are available:
* `BFragmentationProducer`: puts in the EDM event two ValueMaps with weights 
to be used on a jet-by-jet case to reweight the fragmentation function and the semi-leptonic 
branching ratios of the B hadrons according to the uncertainties
* `BFragmentationAnalyzer`: allows to create some simple histograms
with the b-fragmentation momentum transfer functions and the number of semi-leptonically decaying B hadrons
in the simulation

# Running the plugins

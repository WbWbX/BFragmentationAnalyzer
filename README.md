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
* `BFragmentationAnalyzer`: allows to create some simple histograms
with the b-fragmentation momentum transfer functions and the number of semi-leptonically decaying B hadrons
in the simulation
* `BFragmentationProducer`: puts in the EDM event two ValueMaps with weights 
to be used on a jet-by-jet case to reweight the fragmentation function and the semi-leptonic 
branching ratios of the B hadrons according to the uncertainties

# Running the plugins
The analyzer can be run on the output of the pseudo-top producer.
The example below showers some Pohweg LHE events with Pythia8 setting a specific Bowler-Lund parameters.
```
cmsRun test/runBFragmentationAnalyzer_cfg.py rFactB=0.855 outputFile=xb_central.root
```
The producer can also be run on the output of the pseudo-top producer.
The example below shows how to do it starting from a MiniAOD file.
```
cmsRun test/runBFragmentationProducer_cfg.py
```
In your analysis you can use the per-jet weights either by accessing the results of the producer in your analyzer
either by replicating the producer code which basically opens a ROOT file with weights and evaluates them
depending on the xb variable of a b-jet or if it contains or not a semi-leptonic decay.
For the first case an example is provided below.

## Accessing the weights in a EDM analyzer


# Expert notes
To create the weights file one needs to run the  `BFragmentationAnalyzer` on the different fragmentation 
scenarios needed to estimate the fragmentation/semi-leptonic BR systematics.
An example is given by 
```
python test/runWeightCreationLoop.py
```
This will output several ROOT files, one per scenario which can be used to obtain the ratio with respect to the nominal scenario
used in the official CMSSW productions. A script is provided to deploy the weights file under `data` and can be run as
```
python test/buildWeightFile.py 
```
The weights file will contain TGraph objects which can be used to reweight the fragmentation function based on xb=pT(B)/pT(b jet)
and the inclusive semi-leptonic branching ratios of the B hadrons. 
The first is based on the tuning to LEP/SLD data described in https://gitlab.cern.ch/cms-gen/Tuning/merge_requests/2.
The latter is based on the comparison between  the PDG values (http://pdglive.lbl.gov/Viewer.action) 
and the Pythia8 decay tables (http://home.thep.lu.se/~torbjorn/pythia82html/ParticleData.html).
The information is summarized below

| Particle      | Pythia8       | PDG           |
| ------------- | ------------- | ------------- |
| B+            | 0.1129        | 0.1099+-0.028 |
| B0            | 0.10429       | 0.1033+-0.028 |
| B0s           | 0.093         | 0.0960+-0.008 |
| Lambdab       | 0.077         | 0.1030+-0.022 | 

The figure below summarizes this table and shows the inclusive BR obtained directly from Pythia8
and the envelope assigned to cover the uncertainties and differences in the BRs.

(data/semilepbr_unc.png)
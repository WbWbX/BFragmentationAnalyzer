#!/usr/bin/env python

import os
import ROOT

maxEvents=2000
cfg='${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/test/runBFragmentationAnalyzer_cfg.py'
outf='${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights.root'
tune= [ ('up',1.079), ('central',0.8949), ('down',0.6981)]

#run the analyzer
for tag,rFactB in tune:
    os.system('cmsRun %s maxEvents=%d rFactB=%f outputFile=xb_%s.root'%(cfg,maxEvents,rFactB,tag))

#derive the weights
xb={}
for tag,_ in tune:
    fIn=ROOT.TFile.Open('xb_%s_numEvent%d.root'%(tag,maxEvents))
    xb[tag]=fIn.Get('bfragAnalysis/xb_inc').Clone(tag)
    xb[tag].SetDirectory(0)
    fIn.Close()

#save to file
print 'Fragmentation weights have been saved in',outf
fOut=ROOT.TFile.Open(outf,'RECREATE')
for tag in ['up','down']:
    xb[tag].Divide(xb['central'])
    gr=ROOT.TGraph(xb[tag])
    gr.SetName(tag+'gr')
    gr.SetMarkerStyle(20)
    gr.Write(tag+'gr')
fOut.Close()




#!/usr/bin/env python

import os

TUNES=[ ('up','BL',1.079), ('central','BL',0.8949), ('cuetp8m2t4','BL',0.855), ('down','BL',0.6981),('Peterson','P',0.003271)]
MAXEVENTS=500000
CFG='${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/test/runBFragmentationAnalyzer_cfg.py'

def main():

    #run the analyzer
    for tag,frag,param in TUNES:
        os.system('cmsRun %s maxEvents=%d frag=%s param=%f outputFile=xb_%s.root'%(CFG,MAXEVENTS,frag,param,tag))

if __name__ == "__main__":
    main()





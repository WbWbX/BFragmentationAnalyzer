#!/usr/bin/env python

import ROOT
from runWeightCreationLoop import TUNES

def main():

    #derive the weights
    xb={}
    for tag,_,_ in TUNES:
        fName='xb_%s_numEvent%d.root'%(tag,maxEvents) if maxEvents>0 else 'xb_%s.root'%tag
        fIn=ROOT.TFile.Open(fName)
        xb[tag]=fIn.Get('bfragAnalysis/xb_inc').Clone(tag)
        xb[tag].SetDirectory(0)
        fIn.Close()

    #save to file
    print 'Fragmentation weights been saved in',outf
    fOut=ROOT.TFile.Open(outf,'RECREATE')
    for tag in ['up','central','down','Peterson']:
        xb[tag].Divide(xb['cuetp8m2t4'])
        gr=ROOT.TGraph(xb[tag])
        gr.SetName(tag+'gr')
        gr.SetMarkerStyle(20)
        gr.Write(tag+'gr')
    fOut.Close()

if __name__ == "__main__":
    main()

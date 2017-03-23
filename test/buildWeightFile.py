#!/usr/bin/env python

import ROOT
from runWeightCreationLoop import TUNES,MAXEVENTS

BRCEN=0.115583
BRDOWN=0.1033-0.028
BRUP=0.1099+0.028

"""
Interpolate extremes and then derive the weights based on a 2nd order spline for the remaining nodes
"""
def smoothWeights(gr):

    #interpolate for low xb
    gr.Fit('pol9','QR+','',0,0.6)
    lowxb=gr.GetFunction('pol9')

    #flatten tail for xb>1
    gr.Fit('pol0','QR+','',1.03,2)
    highxb=gr.GetFunction('pol0')

    smoothExtremesGr=ROOT.TGraph()
    x,y=ROOT.Double(0),ROOT.Double(0)
    for i in xrange(0,gr.GetN()):
        gr.GetPoint(i,x,y)
        if x<0.55:
            smoothExtremesGr.SetPoint(i,x,lowxb.Eval(x))
        elif x>1.03:
            smoothExtremesGr.SetPoint(i,x,highxb.Eval(x))
        else:
            smoothExtremesGr.SetPoint(i,x,y)

    #smooth the weights
    tSpline=ROOT.TMVA.TSpline2("spline",smoothExtremesGr)
    smoothGr=ROOT.TGraph()
    for i in xrange(0,1000):
        x=2.0*i/1000
        smoothGr.SetPoint(i,x,tSpline.Eval(x))
    return smoothGr


def main():

    outf='${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights.root'
    
    #derive the weights
    xb={}
    for tag,_,_ in TUNES:
        fName='xb_%s_numEvent%d.root'%(tag,MAXEVENTS) if MAXEVENTS>0 else 'xb_%s.root'%tag
        fIn=ROOT.TFile.Open(fName)
        xb[tag]=fIn.Get('bfragAnalysis/xb_inc').Clone(tag)
        xb[tag].SetDirectory(0)
        fIn.Close()

    #save to file
    fOut=ROOT.TFile.Open(outf,'RECREATE')
    for tag in ['up','central','down','Peterson']:
        xb[tag].Divide(xb['cuetp8m2t4'])
        gr=ROOT.TGraphErrors(xb[tag])
        gr.SetMarkerStyle(20)

        sgr=smoothWeights(gr)
        sgr.SetName(tag+'frag')
        sgr.SetLineColor(ROOT.kBlue)
        sgr.Write()

        #gr.Draw('ap')
        #sgr.Draw('l')
        #raw_input()

    #semi-leptonic BRs
    semilepbrUp=ROOT.TGraph()
    semilepbrUp.SetName("semilepbrUp")
    semilepbrUp.SetPoint(0,(1-BRUP)/(1-BRCEN),1.0)
    semilepbrUp.SetPoint(1,BRUP/BRCEN,1.0)
    semilepbrUp.Write()

    semilepbrDown=ROOT.TGraph()
    semilepbrDown.SetName("semilepbrDown")
    semilepbrDown.SetPoint(0,(1-BRDOWN)/(1-BRCEN),0.95)
    semilepbrDown.SetPoint(1,BRDOWN/BRCEN,1.02)
    semilepbrDown.Write()
        

    fOut.Close()
    print 'Fragmentation been saved to',outf

if __name__ == "__main__":
    main()

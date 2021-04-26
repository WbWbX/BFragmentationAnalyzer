#!/usr/bin/env python

import ROOT

from buildBRweights import BRs

def getPythia8Envelope():
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    
    c=ROOT.TCanvas('c','c',500,500)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    c.SetRightMargin(0.05)
    c.SetLeftMargin(0.1)

    frame=ROOT.TH1F('frame',';BR(X#rightarrowl#nuX)',1,0.06,0.15)
    frame.GetYaxis().SetRangeUser(0,4)
    frame.GetYaxis().SetNdivisions(0)
    frame.Draw()

    txt=ROOT.TLatex()
    txt.SetTextFont(42)
    txt.SetTextSize(0.04)

    gr_pdg=ROOT.TGraphErrors()
    gr_pdg.SetName('pdg')
    gr_pdg.SetTitle('PDG 2020')
    gr_pdg.SetMarkerStyle(20)
    gr_py8=ROOT.TGraphErrors()
    gr_py8.SetName('py8')
    gr_py8.SetTitle('Pythia8')
    gr_py8.SetMarkerStyle(24)
    gr_py8env=ROOT.TGraphAsymmErrors()
    gr_py8env.SetName('py8env')
    gr_py8env.SetTitle('Pythia8 env')
    gr_py8env.SetFillStyle(3001)
    gr_py8env.SetFillColor(ROOT.kGray)
    xpdg,xpy8,y=ROOT.Double(0),ROOT.Double(0),ROOT.Double(0)
    for entry in BRs:

        i=gr_py8env.GetN()
        pid,pname,py8inc,py8exc,pdg,pdgUnc=entry

        gr_py8env.SetPoint(i,py8exc,i+0.5)
        gr_py8env.SetPointError(i,
                                ROOT.TMath.Max(py8exc-(pdg-pdgUnc),0.),
                                ROOT.TMath.Max((pdg+pdgUnc)-py8exc,0.),
                                0.5,
                                0.5)

        gr_py8.SetPoint(i,py8exc,i+0.7)
        gr_py8.SetPointError(i,0.,0.)
        
        gr_pdg.SetPoint(i,pdg,i+0.3)
        gr_pdg.SetPointError(i,pdgUnc,0.)

        txt.DrawLatex(0.135,i+0.5,pname)

    gr_py8env.Draw('e2')
    gr_pdg.Draw('p')
    gr_py8.Draw('p')
    
    leg=ROOT.TLegend(0.15,0.4,0.4,0.2)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.AddEntry(gr_pdg,gr_pdg.GetTitle(),'ep')
    leg.AddEntry(gr_py8,gr_py8.GetTitle(),'p')
    leg.Draw()
    
    c.Modified()
    c.Update()
    c.SaveAs('${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/data/semilepbr_unc.pdf')
    c.SaveAs('${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/data/semilepbr_unc.png')
    

def main():
    getPythia8Envelope()

if __name__ == "__main__":
    main()

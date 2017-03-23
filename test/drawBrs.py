#!/usr/bin/env python

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

c=ROOT.TCanvas('c','c',500,500)
c.SetTopMargin(0.05)
c.SetBottomMargin(0.1)
c.SetRightMargin(0.05)
c.SetLeftMargin(0.1)

pdg=ROOT.TGraphErrors()
pdg.SetName('pdg')
pdg.SetTitle('PDG 2016')
pdg.SetMarkerStyle(20)
pdg.SetPoint(0,0.1099,0.3)
pdg.SetPointError(0,0.028,0.)
pdg.SetPoint(1,0.1033,1.3)
pdg.SetPointError(1,0.028,0.)
pdg.SetPoint(2,0.096,2.3)
pdg.SetPointError(2,0.008,0.)
pdg.SetPoint(3,0.103,3.3)
pdg.SetPointError(3,0.022,0.)

py8=ROOT.TGraphErrors()
py8.SetName('py8')
py8.SetTitle('Pythia8')
py8.SetMarkerStyle(24)
py8.SetPoint(0,0.1129,0.7)
py8.SetPointError(0,0.0,0.)
py8.SetPoint(1,0.10429,1.7)
py8.SetPointError(1,0.0,0.)
py8.SetPoint(2,0.093,2.7)
py8.SetPointError(2,0.0,0.)
py8.SetPoint(3,0.077,3.7)
py8.SetPointError(3,0.0,0.)

brcen=0.115583
brdown=0.1033-0.028
brup=0.1099+0.028

py8inc=ROOT.TGraphAsymmErrors()
py8inc.SetName('py8inc')
py8inc.SetTitle('Pythia8 inc')
py8inc.SetMarkerColor(ROOT.kRed)
py8inc.SetLineColor(ROOT.kRed)
py8inc.SetLineWidth(2)
py8inc.SetMarkerStyle(24)
py8inc.SetPoint(0,brcen,4.7)
py8inc.SetPointError(0,brcen-brdown,brup-brcen,0.,0.)

py8env=ROOT.TGraph()
py8env.SetName('py8env')
py8env.SetTitle('Pythia8 env')
py8env.SetFillStyle(3001)
py8env.SetFillColor(ROOT.kGray)
py8env.SetPoint(0,brdown,0)
py8env.SetPoint(1,brdown,5)
py8env.SetPoint(2,brup,5)
py8env.SetPoint(3,brup,0)
py8env.SetPoint(4,brdown,0)


frame=ROOT.TH1F('frame',';BR(X#rightarrowl#nuX)',1,0.05,0.18)
frame.GetYaxis().SetRangeUser(0,5)
frame.GetYaxis().SetNdivisions(0)
frame.Draw()
py8env.Draw('f')
pdg.Draw('p')
py8.Draw('p')
py8inc.Draw('p')

txt=ROOT.TLatex()
txt.SetTextFont(42)
txt.SetTextSize(0.04)
txt.DrawLatex(0.15,0.5,'B^{+}')
txt.DrawLatex(0.15,1.5,'B^{0}')
txt.DrawLatex(0.15,2.5,'B^{0}_{s}')
txt.DrawLatex(0.15,3.5,'#Lambda_{b}')
txt.DrawLatex(0.15,4.5,'#splitline{Pythia8 inc.}{+envelope}')
txt.DrawLatex(0.15,4.1,'#scale[0.8]{%3.3f^{+%3.3f}_{-%3.3f}}'%(brcen,brup-brcen,brcen-brdown))

c.Modified()
c.Update()
c.SaveAs('${CMSSW_BASE}/src/TopQuarkAnalysis/BFragmentationAnalyzer/data/semilepbr_unc.png')

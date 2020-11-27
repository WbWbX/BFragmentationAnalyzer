#!/usr/bin/env python

import argparse
import os

import ROOT

BRs = [
    #   PDGID, name,          py8_incl,py8_excl, pdg,    pdgUnc
        (511,  'B^{0}',       0.23845, 0.1043,   0.1033, 0.0028),
        (521,  'B^{+}',       0.25579, 0.1129,   0.1099, 0.0028),
        (531,  'B^{0}_{s}',   0.21920, 0.0930,   0.0960, 0.008),
        (5122, '#Lambda_{b}', 0.17870, 0.0770,   0.109,  0.022)
    ]
# where
# py8_incl = sum(BR(H -> l nu X)) over lepton flavours, including tau
# py8_excl = BR(H -> l nu X) for l = e or mu
# pdg is excl

def main(inPath, outPath):
    fIn = ROOT.TFile.Open(inPath)
    semiLepMonitor = fIn.Get('bfragAnalysis/semilepbr').Clone('semiLepMonitor')
    semiLepMonitorInc = fIn.Get('bfragAnalysis/semilepbrinc').Clone('semiLepMonitorInc')
    semiLepMonitorNorm = fIn.Get('bfragAnalysis/semilepbr_norm').Clone('semiLepMonitorNorm')
    semiLepMonitor.SetDirectory(0)
    semiLepMonitorInc.SetDirectory(0)
    semiLepMonitorNorm.SetDirectory(0)
    fIn.Close()
    
    fOut = ROOT.TFile.Open(outPath, 'recreate')

    #semi-leptonic BRs
    semilepbrUp = ROOT.TGraph()
    semilepbrUp.SetName("semilepbrup")
    semilepbrDown = ROOT.TGraph()
    semilepbrDown.SetName("semilepbrdown")

    print("PDGID NAME         PY8INC   PY8EXCL  MONBRINC MONBR    PDG      PDGUNC   FRACINC  FRAC    ")
    for entry in BRs:
        i = semilepbrUp.GetN()
        pid,name,py8inc,py8exc,pdg,pdgUnc = entry

        # Compute weights based on PDG/PY8 values
        # There's 1 weight to apply for B decays with semileptonic decay, 1 weight for the rest,
        # to keep the overall normalization constant (=only change the branchin ratio)
        brUp = py8inc * (1 + ROOT.TMath.Max((pdg + pdgUnc) - py8exc, 0.)/py8exc)
        semilepbrUp.SetPoint(i,   -pid, (1 - brUp)/(1 - py8inc))
        semilepbrUp.SetPoint(i+1,  pid, brUp/py8inc)

        brDown = py8inc * (1 - ROOT.TMath.Max(py8exc - (pdg - pdgUnc), 0.)/py8exc)
        semilepbrDown.SetPoint(i,   -pid, (1 - brDown)/(1 - py8inc))
        semilepbrDown.SetPoint(i+1,  pid, brDown/py8inc)

        for ib in range(2, semiLepMonitor.GetNbinsX() + 1):
            if semiLepMonitor.GetXaxis().GetBinLabel(ib) == str(pid):
                monBR = semiLepMonitor.GetBinContent(ib) / semiLepMonitorNorm.GetBinContent(ib) / 2. # divide by 2 to have only 1 lepton flavour
                monBRInc = semiLepMonitorInc.GetBinContent(ib) / semiLepMonitorNorm.GetBinContent(ib)
                frac = semiLepMonitor.GetBinContent(ib) / semiLepMonitor.GetBinContent(1)
                fracInc = semiLepMonitorInc.GetBinContent(ib) / semiLepMonitorInc.GetBinContent(1)
                print("{:<5} {:<12} {:<8} {:<8} {:<8.5f} {:<8.5f} {:<8} {:<8} {:<8.5f} {:<8.5f}".format(pid, name, py8inc, py8exc, monBRInc, monBR, pdg, pdgUnc, fracInc, frac))

    semilepbrUp.Write()
    semilepbrDown.Write()

    fOut.Close()
    print('Fragmentation been saved to {}'.format(outPath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input folder containing merged output ROOT files from condor jobs')
    parser.add_argument('-o', '--output', default=os.path.join(os.getenv("CMSSW_BASE"), "src/TopQuarkAnalysis/BFragmentationAnalyzer/data/bdecayweights.root"), help='Output ROOT file containing weights')
    args = parser.parse_args()

    main(args.input, args.output)


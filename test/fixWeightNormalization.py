#!/usr/bin/env python

import argparse
import os
import numpy as np

import ROOT

from buildWeightFile import TUNES, REF

def fix1Dnorm(inPath, outPath, normPath):
    inFile = ROOT.TFile.Open(inPath)
    outFile = ROOT.TFile.Open(outPath, "recreate")
    normFile = ROOT.TFile.Open(normPath)

    x,y = ROOT.Double(0), ROOT.Double(0)

    norm_ref = normFile.Get("bfragAnalysis/norm").GetBinContent(1)

    for tune in TUNES:
        norm_tune = normFile.Get("bfragAnalysis/debug_norm_frag{}".format(tune)).GetBinContent(1)
        ratio = norm_ref / norm_tune
        print("Rescaling {} by {}".format(tune, ratio))

        rawGr = inFile.Get("frag{}".format(tune))
        outFile.cd()
        rawGr.Write("frag{}".format(tune))

        smoothGr = inFile.Get("frag{}_smooth".format(tune))
        for i in range(smoothGr.GetN()):
            smoothGr.GetPoint(i, x, y)
            smoothGr.SetPoint(i, x, y * ratio)
        smoothGr.Write("frag{}_smooth".format(tune))

    inFile.Close()
    outFile.Close()
    normFile.Close()

def fix2Dnorm(inPath, outPath, normPath):
    inFile = ROOT.TFile.Open(inPath)
    outFile = ROOT.TFile.Open(outPath, "recreate")
    normFile = ROOT.TFile.Open(normPath)

    xb_pt_ref = normFile.Get("bfragAnalysis/xb_pt_lead_B")
    pt_ref = xb_pt_ref.ProjectionY("pt_ref", 0, -1, "e")

    for tune in TUNES:
        print("")

        xb_pt_tune = normFile.Get("bfragAnalysis/debug_xb_pt_lead_B_frag{}VsPt".format(tune))
        pt_tune = xb_pt_tune.ProjectionY("pt_{}".format(tune), 0, -1, "e")

        weights_tune = inFile.Get("frag" + tune)
        weights_tune_smooth = inFile.Get("frag" + tune + "_smooth")

        for ipt in range(1, pt_tune.GetNbinsX() + 1):
            ratio = pt_ref.GetBinContent(ipt) / pt_tune.GetBinContent(ipt)
            print("Rescaling {} in pT bin {} by {}".format(tune, ipt, ratio))
            for jx in range(1, xb_pt_tune.GetNbinsX() + 1):
                orig = weights_tune_smooth.GetBinContent(jx, ipt)
                weights_tune_smooth.SetBinContent(jx, ipt, orig * ratio)

        outFile.cd()
        weights_tune.Write()
        weights_tune_smooth.Write()

    inFile.Close()
    outFile.Close()
    normFile.Close()

if __name__ == "__main__":
    fn1 = "bfragweights.root"
    fn2 = "bfragweights_vs_pt.root"

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input folder containing {} and {} with weights to be re-normalized'.format(fn1, fn2))
    parser.add_argument('-d', '--debug', help='xb_{}.root from a debug run'.format(REF))
    parser.add_argument('-o', '--output', default=os.path.join(os.getenv("CMSSW_BASE"), "src/TopQuarkAnalysis/BFragmentationAnalyzer/data/"), help='Output folder for new weight files')
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    fix1Dnorm(os.path.join(args.input, fn1), os.path.join(args.output, fn1), args.debug)
    fix2Dnorm(os.path.join(args.input, fn2), os.path.join(args.output, fn2), args.debug)

    print('New fragmentation weights saved to {}'.format(args.output))

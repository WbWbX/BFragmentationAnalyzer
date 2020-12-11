#!/usr/bin/env python

import argparse
import os
import numpy as np
from scipy import interpolate

import ROOT

TUNES = [
    'CP5BLup', 'CP5BL', 'CP5BLdown',
    'CP5Peterson', 'CP5Petersonup', 'CP5Petersondown',
    'CUETP8M2T4BL', 'CUETP8M2T4BLdefault',
    'CUETP8M2T4BLLHC', 'CUETP8M2T4BLLHCup', 'CUETP8M2T4BLLHCdown',
]
# all ratios will be computed with the following as reference
REF = 'CP5BLdefault'

# above that xb value, will apply different treatment
THRES = 1.
# upper edge along xb axis
MAX = 1.5

from contextlib import contextmanager
@contextmanager
def returnToDirectory():
    gpwd = ROOT.gDirectory.GetPath()
    yield
    ROOT.gDirectory.cd(gpwd)


def smoothWeights(ratio, ref, to1AboveThres=False):
    """ Derive the weights based on a 2nd order spline below the threshold, keep original values above (or set to 1 if to1AboveThres is True) """

    gr = ROOT.TGraphErrors(ratio)

    smoothExtremesGr = ROOT.TGraph()
    x,y = ROOT.Double(0), ROOT.Double(0)
    for i in range(0, gr.GetN()):
        gr.GetPoint(i, x, y)
        if x <= THRES:
            smoothExtremesGr.SetPoint(i, x, y)

    #smooth the weights
    smoothGr = ROOT.TGraph()
    tSpline = ROOT.TMVA.TSpline2("spline", smoothExtremesGr)
    nPtsLow = 300
    for i in range(0, nPtsLow):
        x = THRES * float(i) / nPtsLow
        smoothGr.SetPoint(i, x, max(0., tSpline.Eval(x)))
        smoothGr.SetPoint
    nPtsHigh = 20
    for i in range(0, nPtsHigh):
        x = THRES + (MAX - THRES) * float(i) / nPtsHigh
        if to1AboveThres:
            y = 1.
        else:
            y = ratio.GetBinContent(ratio.GetXaxis().FindBin(x))
        smoothGr.SetPoint(nPtsLow + i, x, y)
        if i == nPtsHigh - 1.:
            x += 1. / nPtsHigh
        smoothGr.SetPoint(nPtsLow + nPtsHigh, x, y)

    # make sure applying the smoothed weights leaves the normalization unchanged
    reweight = ref.Clone(ref.GetName() + "_weighted")
    for i in range(1, ref.GetNbinsX() + 1):
        x = reweight.GetXaxis().GetBinCenter(i)
        weight = smoothGr.Eval(x)
        reweight.SetBinContent(i, weight * reweight.GetBinContent(i))
    norm = reweight.Integral() / ref.Integral()
    print("Rescaling {} by {}".format(ratio.GetName(), 1./norm))

    x,y = ROOT.Double(0), ROOT.Double(0)
    for i in range(smoothGr.GetN()):
        smoothGr.GetPoint(i, x, y)
        smoothGr.SetPoint(i, x, y / norm)

    return smoothGr

def smoothWeightsAkima(ratio, ref, to1AboveThres=False):
    """ Derive the weights based on Akima sub-spline below the threshold, keep original values above (or set to 1 if to1AboveThres is True) """

    x_hist = [ ratio.GetXaxis().GetBinCenter(i) for i in range(1, ratio.GetXaxis().GetNbins() + 1) ]
    x_hist = [x for x in x_hist if x <= THRES ]
    x = np.array([0.] + x_hist + [THRES])
    y_hist = [ ratio.GetBinContent(i) for i in range(1, ratio.GetNbinsX() + 1) if ratio.GetXaxis().GetBinCenter(i) <= THRES ]
    y = np.array([y_hist[0]] + y_hist + [y_hist[-1]])

    spline = interpolate.Akima1DInterpolator(x, y)

    x_detail = np.linspace(0, THRES, 300, endpoint=True, dtype=np.float64)
    y_detail = spline(x_detail)

    smoothGr = ROOT.TGraph(len(x_detail), x_detail, y_detail)

    # make sure applying the smoothed weights leaves the normalization unchanged
    reweight = ref.Clone(ref.GetName() + "_weighted")
    for i in range(1, ref.GetNbinsX() + 1):
        x = reweight.GetXaxis().GetBinCenter(i)
        if x >= THRES:
            weight = 1
        else:
            weight = smoothGr.Eval(x)
        # print("x={}, weight={}".format(x, weight))
        reweight.SetBinContent(i, weight * reweight.GetBinContent(i))
    norm = reweight.Integral() / ref.Integral()
    print("Rescaling {} by {}".format(ratio.GetName(), 1./norm))

    x,y = ROOT.Double(0), ROOT.Double(0)
    for i in range(smoothGr.GetN()):
        smoothGr.GetPoint(i, x, y)
        smoothGr.SetPoint(i, x, y / norm)

    return smoothGr

def th1SmoothRange(hist, nTimes, xMin, xMax):
    """ Smooth hist nTimes but only within [xMin,xMax] (should coincide with bin edges!) """
    axis = hist.GetXaxis()
    oldFirst,oldLast = 1,axis.GetNbins()
    lastBin = axis.FindBin(xMax)
    if xMax == axis.GetBinLowEdge(lastBin):
        lastBin -= 1
    axis.SetRange(axis.FindBin(xMin), lastBin)
    hist.Smooth(nTimes, "r")
    axis.SetRange(oldFirst, oldLast)

def th1RebinRange(hist, nTimes, xMin, xMax, suffix="_rebin"):
    """ Rebin hist nTimes but only within [xMin,xMax] (return new histogram) """

    origName = hist.GetName()
    axis = hist.GetXaxis()
    oldBins = [ axis.GetBinLowEdge(i) for i in range(1, axis.GetNbins() + 2) ]
    binsInRange = [ x for x in oldBins if x >= xMin and x <= xMax ]
    if (len(binsInRange) - 1) % nTimes != 0:
        raise RuntimeError("Histogram {} has {} bins within range, cannot be rebinned {} times".format(origName, len(binsInRange) - 1, nTimes))
    newBins = []
    for x in oldBins:
        if x <= xMin:
            newBins.append([x])
        elif x <= xMax:
            if len(newBins[-1]) == nTimes:
                newBins.append([x])
            else:
                newBins[-1].append(x)
        else:
            newBins.append([x])
    newBins = [ b[0] for b in newBins ]
    return hist.Rebin(len(newBins) - 1, origName + suffix, np.array(newBins, dtype=np.float64))

def toDensity(hist):
    """ Transform "count" histogram into "density" histogram: divide bin entries by bin widths and normalize to 1 """
    for i in range(1, hist.GetNbinsX() + 1):
        width = hist.GetBinWidth(i)
        hist.SetBinContent(i, hist.GetBinContent(i) / width)
        hist.SetBinError(i, hist.GetBinError(i) / width)
    integral = hist.Integral()
    if integral > 0:
        hist.Scale(1./integral)

def loadAllHists(inDir, name):
    xb = {}
    for tag in TUNES + [REF]:
        with returnToDirectory():
            fName = os.path.join(inDir, 'xb_{}.root'.format(tag))
            fIn = ROOT.TFile.Open(fName)
            xb[tag] = fIn.Get(name).Clone("xb_" + tag)
            xb[tag].SetDirectory(0)
            fIn.Close()
    return xb

def buildAndWriteWeights(inDir, outDir):
    fOut = ROOT.TFile.Open(os.path.join(outDir, "bfragweights.root"), 'recreate')

    xb = loadAllHists(inDir, "bfragAnalysis/xb_lead_B")

    toDensity(xb[REF])
    #save to file
    ref_smoothed = xb[REF].Clone(xb[REF].GetName() + "_smooth")
    th1SmoothRange(ref_smoothed, 2, 0., THRES)
    for tag in TUNES:
        toDensity(xb[tag])
        ratio = xb[tag].Clone(xb[tag].GetName() + "_ratio")
        ratio.Divide(xb[REF])
        raw_gr = ROOT.TGraphErrors(ratio)
        raw_gr.SetMarkerStyle(20)
        raw_gr.SetName("frag{}".format(tag))
        raw_gr.SetLineColor(ROOT.kBlue)
        raw_gr.Write()

        th1SmoothRange(xb[tag], 2, 0., THRES)
        xb[tag].Divide(ref_smoothed)
        # sgr = smoothWeights(xb[tag], xb[REF])
        sgr = smoothWeightsAkima(xb[tag], xb[REF], to1AboveThres=True) # interpolate using Akima subspline, set weight to 1 above xb=1
        sgr.SetName("frag{}_smooth".format(tag))
        sgr.SetLineColor(ROOT.kRed)
        sgr.Write()

    fOut.Close()

def buildAndWrite2DWeights(inDir, outDir):
    fOut = ROOT.TFile.Open(os.path.join(outDir, "bfragweights_vs_pt_debug.root"), 'recreate')
    
    xb = loadAllHists(inDir, "bfragAnalysis/xb_pt_lead_B")

    ptBins = [ xb[REF].GetYaxis().GetBinLowEdge(i) for i in range(1, xb[REF].GetYaxis().GetNbins() + 2) ]
    ptBins = np.array(ptBins)

    xb_split = {}
    for tag,hist in xb.items():
        hists = {}
        yaxis = hist.GetYaxis()
        for i in range(1, yaxis.GetNbins() + 1):
            start,stop = yaxis.GetBinLowEdge(i),yaxis.GetBinUpEdge(i)
            if start < ptBins[-2]:
                ptRange = "pT{:.0f}To{:.0f}".format(start, stop)
                proj = hist.ProjectionX(hist.GetName() + "_" + ptRange, i, i, "e")
                hists[ptRange] = proj
            else:
                ptRange = "pT{:.0f}".format(start)
                proj = hist.ProjectionX(hist.GetName() + "_" + ptRange, i, yaxis.GetNbins() + 1, "e")
                hists[ptRange] = proj
        # ad-hoc rebinnings
        hists["pT20To40"] = th1RebinRange(hists["pT20To40"], 2, 0., THRES, suffix="")
        hists["pT40To60"] = th1RebinRange(hists["pT40To60"], 2, 0., THRES, suffix="")
        hists["pT150To200"] = th1RebinRange(hists["pT150To200"], 2, 0., THRES, suffix="")
        hists["pT200To350"] = th1RebinRange(hists["pT200To350"], 3, 0., THRES, suffix="")
        hists["pT350To500"] = th1RebinRange(hists["pT350To500"], 4, 0., THRES, suffix="")
        hists["pT500"] = th1RebinRange(hists["pT500"], 5, 0., THRES, suffix="")
        for proj in hists.values():
            toDensity(proj)
            proj.Write()
        xb_split[tag] = hists

    refs_smoothed = { ptRange: xb_split[REF][ptRange].Clone(xb_split[REF][ptRange].GetName() + "_smooth") for ptRange in xb_split[REF] }
    for hist in refs_smoothed.values():
        th1SmoothRange(hist, 2, 0., THRES) # smooth reference hists between 0 and 1

    raw_graphs = { tag: {} for tag in TUNES }
    smooth_graphs = { tag: {} for tag in TUNES }

    for tag in TUNES:
        for ptRange,hist in xb_split[tag].items():
            ratio = hist.Clone(hist.GetName() + "_ratio")
            ratio.Divide(xb_split[REF][ptRange])
            raw_gr = ROOT.TGraphErrors(ratio)
            raw_gr.SetMarkerStyle(20)
            raw_gr.SetName("frag{}_{}".format(tag, ptRange))
            raw_gr.SetLineColor(ROOT.kBlue)
            raw_gr.Write()
            raw_graphs[tag][ptRange] = raw_gr

            ref_smooth = refs_smoothed[ptRange]
            th1SmoothRange(hist, 2, 0., THRES) # smooth target hists between 0 and 1 before dividing
            hist.Divide(ref_smooth)
            raw_sgr = ROOT.TGraphErrors(hist)
            raw_sgr.SetMarkerStyle(20)
            raw_sgr.SetName("frag{}_{}_rawSmooth".format(tag, ptRange)) # "rawSmooth" = only histogram smoothing, no spline
            raw_sgr.SetLineColor(ROOT.kGreen)
            raw_sgr.Write()
            sgr = smoothWeightsAkima(hist, ref_smooth, to1AboveThres=True) # interpolate using Akima subspline, set weight to 1 above xb=1
            sgr.SetName("frag{}_{}_smooth".format(tag, ptRange))
            sgr.SetLineColor(ROOT.kRed)
            sgr.Write()
            smooth_graphs[tag][ptRange] = sgr

    fOut.Close()

    fOut = ROOT.TFile.Open(os.path.join(outDir, "bfragweights_vs_pt.root"), 'recreate')
    
    xbBins = np.linspace(0, THRES, 300, endpoint=True)
    for tag in TUNES:
        raw_th2 = ROOT.TH2F("frag{}".format(tag), "", len(xbBins) - 1, xbBins, len(ptBins) - 1, ptBins)
        smooth_th2 = ROOT.TH2F("frag{}_smooth".format(tag), "", len(xbBins) - 1, xbBins, len(ptBins) - 1, ptBins)
        for i,pt in enumerate(ptBins[:-1]):
            if pt == ptBins[-2]:
                ptRange = "pT{:.0f}".format(pt)
            else:
                ptRange = "pT{:.0f}To{:.0f}".format(pt, ptBins[i+1])
            for j,xb in enumerate(xbBins):
                raw_th2.SetBinContent(j + 1, i + 1, raw_graphs[tag][ptRange].Eval(xb))
                smooth_th2.SetBinContent(j + 1, i + 1, smooth_graphs[tag][ptRange].Eval(xb))
        raw_th2.Write()
        smooth_th2.Write()

    fOut.Close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input folder containing merged output ROOT files from condor jobs')
    parser.add_argument('-o', '--output', default=os.path.join(os.getenv("CMSSW_BASE"), "src/TopQuarkAnalysis/BFragmentationAnalyzer/data/"), help='Output folder')
    args = parser.parse_args()

    buildAndWriteWeights(args.input, args.output)
    buildAndWrite2DWeights(args.input, args.output)
    print('Fragmentation been saved to {}'.format(args.output))

#! /bin/env python

import os, sys, argparse
import numpy as np

# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []

# ROOT imports
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

from buildWeightFile import toDensity, th1SmoothRange

# colors = ['#468966', '#8E2800']
colors = [
    "#7044f1",
    "#45ad95",
    "#c07f00",
    "#da7fb7",
    "#ff2719",
    "#251c00",
    "#A2D729",
    "#FF1053",
    "#fa824c"]
nominal_color = ROOT.TColor.GetColor('#FFB03B')

def setTDRStyle():
  tdrStyle =  ROOT.TStyle("tdrStyle","Style for P-TDR")

   #for the canvas:
  tdrStyle.SetCanvasBorderMode(0)
  tdrStyle.SetCanvasColor(ROOT.kWhite)
  tdrStyle.SetCanvasDefH(600) #Height of canvas
  tdrStyle.SetCanvasDefW(600) #Width of canvas
  tdrStyle.SetCanvasDefX(0)   #POsition on screen
  tdrStyle.SetCanvasDefY(0)


  tdrStyle.SetPadBorderMode(0)
  #tdrStyle.SetPadBorderSize(Width_t size = 1)
  tdrStyle.SetPadColor(ROOT.kWhite)
  tdrStyle.SetPadGridX(False)
  tdrStyle.SetPadGridY(False)
  tdrStyle.SetGridColor(0)
  tdrStyle.SetGridStyle(3)
  tdrStyle.SetGridWidth(1)

#For the frame:
  tdrStyle.SetFrameBorderMode(0)
  tdrStyle.SetFrameBorderSize(1)
  tdrStyle.SetFrameFillColor(0)
  tdrStyle.SetFrameFillStyle(0)
  tdrStyle.SetFrameLineColor(1)
  tdrStyle.SetFrameLineStyle(1)
  tdrStyle.SetFrameLineWidth(1)
  
#For the histo:
  #tdrStyle.SetHistFillColor(1)
  #tdrStyle.SetHistFillStyle(0)
  tdrStyle.SetHistLineColor(1)
  tdrStyle.SetHistLineStyle(0)
  tdrStyle.SetHistLineWidth(1)
  #tdrStyle.SetLegoInnerR(Float_t rad = 0.5)
  #tdrStyle.SetNumberContours(Int_t number = 20)

  tdrStyle.SetEndErrorSize(2)
  #tdrStyle.SetErrorMarker(20)
  #tdrStyle.SetErrorX(0.)
  
  tdrStyle.SetMarkerStyle(20)
  
#For the fit/function:
  tdrStyle.SetOptFit(1)
  tdrStyle.SetFitFormat("5.4g")
  tdrStyle.SetFuncColor(2)
  tdrStyle.SetFuncStyle(1)
  tdrStyle.SetFuncWidth(1)

#For the date:
  tdrStyle.SetOptDate(0)
  # tdrStyle.SetDateX(Float_t x = 0.01)
  # tdrStyle.SetDateY(Float_t y = 0.01)

# For the statistics box:
  tdrStyle.SetOptFile(0)
  tdrStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
  tdrStyle.SetStatColor(ROOT.kWhite)
  tdrStyle.SetStatFont(42)
  tdrStyle.SetStatFontSize(0.025)
  tdrStyle.SetStatTextColor(1)
  tdrStyle.SetStatFormat("6.4g")
  tdrStyle.SetStatBorderSize(1)
  tdrStyle.SetStatH(0.1)
  tdrStyle.SetStatW(0.15)
  # tdrStyle.SetStatStyle(Style_t style = 1001)
  # tdrStyle.SetStatX(Float_t x = 0)
  # tdrStyle.SetStatY(Float_t y = 0)

# Margins:
  tdrStyle.SetPadTopMargin(0.05)
  tdrStyle.SetPadBottomMargin(0.13)
  tdrStyle.SetPadLeftMargin(0.16)
  tdrStyle.SetPadRightMargin(0.02)

# For the Global title:

  tdrStyle.SetOptTitle(0)
  tdrStyle.SetTitleFont(42)
  tdrStyle.SetTitleColor(1)
  tdrStyle.SetTitleTextColor(1)
  tdrStyle.SetTitleFillColor(10)
  tdrStyle.SetTitleFontSize(0.05)
  # tdrStyle.SetTitleH(0) # Set the height of the title box
  # tdrStyle.SetTitleW(0) # Set the width of the title box
  # tdrStyle.SetTitleX(0) # Set the position of the title box
  # tdrStyle.SetTitleY(0.985) # Set the position of the title box
  # tdrStyle.SetTitleStyle(Style_t style = 1001)
  # tdrStyle.SetTitleBorderSize(2)

# For the axis titles:

  tdrStyle.SetTitleColor(1, "XYZ")
  tdrStyle.SetTitleFont(42, "XYZ")
  tdrStyle.SetTitleSize(0.06, "XYZ")
  # tdrStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
  # tdrStyle.SetTitleYSize(Float_t size = 0.02)
  tdrStyle.SetTitleXOffset(0.9)
  tdrStyle.SetTitleYOffset(1.25)
  # tdrStyle.SetTitleOffset(1.1, "Y") # Another way to set the Offset

# For the axis labels:

  tdrStyle.SetLabelColor(1, "XYZ")
  tdrStyle.SetLabelFont(42, "XYZ")
  tdrStyle.SetLabelOffset(0.007, "XYZ")
  tdrStyle.SetLabelSize(0.03, "XYZ")

# For the axis:

  tdrStyle.SetAxisColor(1, "XYZ")
  tdrStyle.SetStripDecimals(True)
  tdrStyle.SetTickLength(0.03, "XYZ")
  tdrStyle.SetNdivisions(510, "XYZ")
  tdrStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
  tdrStyle.SetPadTickY(1)

# Change for log plots:
  tdrStyle.SetOptLogx(0)
  tdrStyle.SetOptLogy(0)
  tdrStyle.SetOptLogz(0)

  tdrStyle.SetCanvasDefH(600) #Height of canvas
  tdrStyle.SetCanvasDefW(540) #Width of canvas
  tdrStyle.SetTitleSize(1, "XYZ")
  tdrStyle.SetLabelSize(0.1, "XYZ")
  tdrStyle.cd()


  return tdrStyle


def drawVariations(name, nominal, variations, title, output, logy=False, nominalName=None, norm=False, ratio_range=None, x_range=None, smooth=0, nom_to_density=False, var_to_density=False, leg_pos="l", ratio_style="hist L"):
    print("Doing {name}, {title}".format(name=name, title=title))

    c = ROOT.TCanvas("c", "c")

    hi_pad = ROOT.TPad("pad_hi", "", 0., 0.33333, 1, 1)
    hi_pad.Draw()
    hi_pad.SetTopMargin(0.05 / .6666)
    hi_pad.SetLeftMargin(0.16)
    hi_pad.SetBottomMargin(0.015)
    hi_pad.SetRightMargin(0.02)

    lo_pad = ROOT.TPad("pad_lo", "", 0., 0., 1, 0.33333)
    lo_pad.Draw()
    lo_pad.SetTopMargin(1)
    lo_pad.SetLeftMargin(0.16)
    lo_pad.SetBottomMargin(0.13 / 0.33333)
    lo_pad.SetRightMargin(0.02)
    lo_pad.SetTickx(1)

    hi_pad.cd()

    nominal.SetLineWidth(2)
    nominal.SetLineStyle(2)
    nominal.SetLineColor(nominal_color)
    nominal.GetYaxis().SetLabelSize(0.02 / 0.666)
    nominal.GetYaxis().SetTitleSize(0.03 / 0.666)
    nominal.GetYaxis().SetTitleOffset(1.7 * 0.666)
    nominal.GetYaxis().SetTitle("a.u.")
    nominal.GetXaxis().SetLabelSize(0)
    if nom_to_density:
        toDensity(nominal)
    if smooth:
        th1SmoothRange(nominal, smooth, 0., 1.)
    if norm:
        nominal.Scale(1./nominal.Integral())
    if x_range:
        nominal.GetXaxis().SetRangeUser(x_range[0], x_range[1])
    nominal.Draw("hist")

    for i, (v, h) in enumerate(variations):
        if var_to_density:
            toDensity(h)
        if smooth:
            th1SmoothRange(h, smooth, 0., 1.)
        if norm:
            h.Scale(1./h.Integral())
        h.SetLineWidth(2)
        h.SetLineColor(ROOT.TColor.GetColor(colors[i]))
        h.Draw("hist same")

    hist_max = -100
    hist_min = 9999999
    for i in range(1, nominal.GetNbinsX() + 1):
        hist_max = max(hist_max, nominal.GetBinContent(i), *[h.GetBinContent(i) for v,h in variations])
        hist_min = min(hist_min, nominal.GetBinContent(i), *[h.GetBinContent(i) for v,h in variations])
    if logy:
        hi_pad.SetLogy()
        nominal.GetYaxis().SetRangeUser(hist_min * 0.9, hist_max * 1.4)
    else:
        nominal.GetYaxis().SetRangeUser(0, hist_max * 1.2)

    lo_pad.cd()
    lo_pad.SetGrid()

    ratios = [ h.Clone() for v,h in variations ]
    for r in ratios:
        r.Divide(nominal)

    ratios[0].GetXaxis().SetLabelSize(0.02 / 0.333)
    ratios[0].GetXaxis().SetTitleSize(0.03 / 0.333)
    ratios[0].GetXaxis().SetLabelOffset(0.05)
    ratios[0].GetXaxis().SetTitleOffset(1.5)
    ratios[0].GetXaxis().SetTitle(title)
    ratios[0].GetYaxis().SetLabelSize(0.02 / 0.333)
    ratios[0].GetYaxis().SetTitleSize(0.03 / 0.333)
    ratios[0].GetYaxis().SetTitleOffset(1.7 * 0.333)
    ratios[0].GetYaxis().SetTitle("")
    ratios[0].GetYaxis().SetNdivisions(502, True)
    ratios[0].GetYaxis().SetRangeUser(0.5, 1.5)
    if x_range:
        ratios[0].GetXaxis().SetRangeUser(x_range[0], x_range[1])

    ratios[0].Draw(ratio_style)

    line = ROOT.TLine(ratios[0].GetXaxis().GetBinLowEdge(1), 1, ratios[0].GetXaxis().GetBinUpEdge(ratios[0].GetXaxis().GetLast()), 1)
    line.Draw("same")

    for i, ratio in enumerate(ratios):
        ratio.SetLineColor(ROOT.TColor.GetColor(colors[i]))
        ratio.SetMarkerSize(0.)
        ratio.SetLineWidth(3)
        ratio.Draw(ratio_style + "same")

    # Look for min and max of ratio and zoom accordingly
    ratio_max = 1.
    ratio_min = 1.
    for i in range(1, ratios[0].GetNbinsX() + 1):
        ratio_max = max(ratio_max, *[r.GetBinContent(i) for r in ratios])
        ratio_min = min(ratio_min, *[r.GetBinContent(i) for r in ratios])

    if ratio_range:
        ratios[0].GetYaxis().SetRangeUser(ratio_range[0], ratio_range[1])
    else:
        ratios[0].GetYaxis().SetRangeUser(0.9 * ratio_min, 1.1 * ratio_max)
    ratios[0].GetYaxis().SetNdivisions(210)
    ratios[0].GetYaxis().SetTitle('Ratio')

    c.cd()
    if leg_pos == "l":
        l = ROOT.TLegend(0.2, 0.7, 0.5, 0.92)
    elif leg_pos == "r":
        l = ROOT.TLegend(0.65, 0.7, 0.95, 0.92)
    else:
        l = ROOT.TLegend(*leg_pos)
    l.SetTextFont(42)
    l.SetFillColor(ROOT.kWhite)
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    l.SetTextSize(0.022)

    l.AddEntry(nominal, nominalName if nominalName else "Nominal" )
    for i,(v,h) in enumerate(variations):
        l.AddEntry(ratios[i], v)
    l.Draw("same")

    c.SaveAs(os.path.join(output, name + ".pdf"))
    hi_pad.Delete()
    lo_pad.Delete()

# Options

parser = argparse.ArgumentParser(description='Draw systematics')
parser.add_argument('-o', '--output', type=str, help='Output directory')
parser.add_argument('-i', '--input', type=str, help='Input directory')

options = parser.parse_args()

if not os.path.isdir(options.output):
    os.makedirs(options.output)

setTDRStyle()

plotCfg = [
    { "name": "bFrag", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default", "vars": [("Tuned B-L central (CP5)", options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), ("Tuned B-L up (CP5)", options.input + "/xb_CP5BLup.root", "bfragAnalysis/xb_lead_B"), ("Tuned B-L down (CP5)", options.input + "/xb_CP5BLdown.root", "bfragAnalysis/xb_lead_B"), ("Tuned Peterson central (CP5)", options.input + "/xb_CP5Peterson.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "ratio-range": [0, 2], "nom_to_density": True, "var_to_density": True },

    { "name": "bFrag_smooth", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default", "vars": [("Tuned B-L central (CP5)", options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), ("Tuned B-L up (CP5)", options.input + "/xb_CP5BLup.root", "bfragAnalysis/xb_lead_B"), ("Tuned B-L down (CP5)", options.input + "/xb_CP5BLdown.root", "bfragAnalysis/xb_lead_B"), ("Tuned Peterson central (CP5)", options.input + "/xb_CP5Peterson.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "smooth": 2, "ratio-range": [0, 2], "nom_to_density": True, "var_to_density": True }, # same as above but smooth histograms twice here
    
    { "name": "bFrag_Peterson", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default", "vars": [("Tuned Peterson central (CP5)", options.input + "/xb_CP5Peterson.root", "bfragAnalysis/xb_lead_B"), ("Tuned Peterson up (CP5)", options.input + "/xb_CP5Petersonup.root", "bfragAnalysis/xb_lead_B"), ("Tuned Peterson down (CP5)", options.input + "/xb_CP5Petersondown.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "ratio-range": [0, 2], "nom_to_density": True, "var_to_density": True },

    { "name": "bFrag_tunes", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default B-L", "vars": [("CP5 tuned B-L central", options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), ("CUETP8M2T4 default B-L", options.input + "/xb_CUETP8M2T4BLdefault.root", "bfragAnalysis/xb_lead_B"), ("CUETP8M2T4 tuned B-L central", options.input + "/xb_CUETP8M2T4BL.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "ratio-range": [0.2, 1.7], "nom_to_density": True, "var_to_density": True },
    
    { "name": "bFrag_old", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CUETP8M2T4BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CUETP8M2T4 default B-L", "vars": [("CUETP8M2T4 tuned B-L central", options.input + "/xb_CUETP8M2T4BL.root", "bfragAnalysis/xb_lead_B"), ("CUETP8M2T4 B-L TOP-18-012", options.input + "/xb_CUETP8M2T4BLLHC.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "ratio-range": [0.7, 1.5], "nom_to_density": True, "var_to_density": True },

    { "name": "bFrag_top-18-012", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default B-L", "vars": [("CUETP8M2T4 B-L TOP-18-012 central", options.input + "/xb_CUETP8M2T4BLLHC.root", "bfragAnalysis/xb_lead_B"), ("CUETP8M2T4 B-L TOP-18-012 up", options.input + "/xb_CUETP8M2T4BLLHCup.root", "bfragAnalysis/xb_lead_B"), ("CUETP8M2T4 B-L TOP-18-012 down", options.input + "/xb_CUETP8M2T4BLLHCdown.root", "bfragAnalysis/xb_lead_B") ], "norm": True, "ratio-range": [0.7, 1.5], "nom_to_density": True, "var_to_density": True },

     { "name": "bFrag_checkBvsInc", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default, leading B", "vars": [("CP5 default, if(leading=B)", options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_inc"), ("Tuned B-L central (CP5), leading B", options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), ("Tuned B-L central (CP5), if(leading=B)", options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_inc") ], "norm": True, "ratio-range": [0.6, 1.4], "nom_to_density": True, "var_to_density": True },
     
    { "name": "bFrag_debug_CP5BL", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 BL central", "vars": [("CP5 BL default to CP5 BL central", options.input + "/xb_CP5BLdefault_debug.root", "bfragAnalysis/debug_xb_lead_B_fragCP5BL") ], "ratio-range": [0.6, 1.4], "ratio-style": "histE0" },
    { "name": "bFrag_debug_CP5Peterson", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5Peterson.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 Peterson central", "vars": [("CP5 BL default to CP5 Peterson central", options.input + "/xb_CP5BLdefault_debug.root", "bfragAnalysis/debug_xb_lead_B_fragCP5Peterson") ], "ratio-range": [0.6, 1.4], "ratio-style": "histE0" },

    { "name": "pt_debug_CP5BL", "title": "p_{T}(jet)", "nominal": (options.input + "/bfragweights_vs_pt_debug.root", "pt_CP5BLdefault"), "nominalName": "CP5 B-L default", "vars": [(leg, options.input + "/bfragweights_vs_pt_debug.root" , hist) for (leg, hist) in zip(["CP5 B-L central", "CP5 B-L up", "CP5 B-L down"], ["pt_CP5BL", "pt_CP5BLup", "pt_CP5BLdown"]) ], "ratio-range": [0.98, 1.02], "norm": True, "x-range": [20, 500], "leg-pos": "r", "ratio-style": "histE0" },
    { "name": "pt_debug_Peterson", "title": "p_{T}(jet)", "nominal": (options.input + "/bfragweights_vs_pt_debug.root", "pt_CP5BLdefault"), "nominalName": "CP5 B-L default", "vars": [(leg, options.input + "/bfragweights_vs_pt_debug.root" , hist) for (leg, hist) in zip(["CP5 Peterson central", "CP5 Peterson up", "CP5 Peterson down"], ["pt_CP5Peterson", "pt_CP5Petersonup", "pt_CP5Petersondown"]) ], "ratio-range": [0.98, 1.02], "norm": True, "x-range": [20, 500], "leg-pos": "r", "ratio-style": "histE0" },
    { "name": "pt_debug_CUETP", "title": "p_{T}(jet)", "nominal": (options.input + "/bfragweights_vs_pt_debug.root", "pt_CP5BLdefault"), "nominalName": "CP5 B-L default", "vars": [(leg, options.input + "/bfragweights_vs_pt_debug.root" , hist) for (leg, hist) in zip(["CUETP8M2T4 B-L default", "CUETP8M2T4 B-L LHC central", "CUETP8M2T4 B-L LHC up", "CUETP8M2T4 B-L LHC down"], ["pt_CUETP8M2T4BL", "pt_CUETP8M2T4BLLHC", "pt_CUETP8M2T4BLLHCup","pt_CUETP8M2T4BLLHCdown"]) ], "ratio-range": [0.97, 1.03], "norm": True, "x-range": [20, 500], "leg-pos": "r", "ratio-style": "histE0" },
]


for plot in plotCfg:
    tf = ROOT.TFile.Open(plot["nominal"][0])
    nominal = tf.Get(plot["nominal"][1])
    print("Doing ", plot["nominal"][1])
    try:
        nominal.SetDirectory(0)
    except AttributeError as e:
        print("Could not load {} from {}".format(plot["nominal"][1], plot["nominal"][0]))
        raise e
    tf.Close()

    variations = []
    for var in plot["vars"]:
        tf = ROOT.TFile.Open(var[1])
        variations.append((var[0], tf.Get(var[2])))
        try:
            variations[-1][1].SetDirectory(0)
        except AttributeError as e:
            print("Could not load {} from {}".format(var[2], var[1]))
            raise e
        tf.Close()

    drawVariations(plot["name"], nominal, variations, plot["title"], options.output, logy=plot.get("log", False), nominalName=plot.get("nominalName", None), norm=plot.get("norm", False), ratio_range=plot.get("ratio-range", None), x_range=plot.get("x-range", None), smooth=plot.get("smooth", 0), nom_to_density=plot.get("nom_to_density", False), var_to_density=plot.get("var_to_density", False), ratio_style=plot.get("ratio-style", "histL"), leg_pos=plot.get("leg-pos", "l"))


#### pT plots

pTbins = [20, 40, 60, 100, 150, 200, 350, 500]
pTranges = ["pT{}To{}".format(pTbins[i], pTbins[i+1]) for i in range(len(pTbins)-1)]
pTranges.append("pT{}".format(pTbins[-1]))

pTplots = [
    { "name": "bFrag_pT_CP5BLdefault", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdefault.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default, averaged", "vars": [("CP5 default, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5BLdefault_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5BL", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BL.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 default, averaged", "vars": [("CP5 nominal, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5BL_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5BLup", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLup.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 up, averaged", "vars": [("CP5 up, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5BLup_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5BLdown", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5BLdown.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 down, averaged", "vars": [("CP5 down, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5BLdown_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5Peterson", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5Peterson.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 Peterson, averaged", "vars": [("CP5 Peterson, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5Peterson_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5Petersonup", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5Petersonup.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 Peterson up, averaged", "vars": [("CP5 Peterson up, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5Petersonup_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
    { "name": "bFrag_pT_CP5Petersondown", "title": "x_{b} = p_{T}(B)/p_{T}(jet)", "nominal": (options.input + "/xb_CP5Petersondown.root", "bfragAnalysis/xb_lead_B"), "nominalName": "CP5 Peterson down, averaged", "vars": [("CP5 Peterson down, {pT}".format(pT=pT), options.input + "/bfragweights_vs_pt_debug.root", "xb_CP5Petersondown_{pT}".format(pT=pT)) for pT in pTranges], "norm": True, "ratio-range": [0, 5.], "ratio-style": "hist" },
]

for plot in pTplots:
    tf = ROOT.TFile.Open(plot["nominal"][0])
    nominal = tf.Get(plot["nominal"][1])
    print("Doing ", plot["nominal"][1])
    try:
        nominal.SetDirectory(0)
    except AttributeError as e:
        print("Could not load {} from {}".format(plot["nominal"][1], plot["nominal"][0]))
        raise e
    tf.Close()
    toDensity(nominal)
    th1SmoothRange(nominal, 2, 0., 1.)
    orig_bins = np.array(nominal.GetXaxis().GetXbins())

    variations = []
    for var in plot["vars"]:
        tf = ROOT.TFile.Open(var[1])
        hist = tf.Get(var[2])
        try:
            hist.SetDirectory(0)
        except AttributeError as e:
            print("Could not load {} from {}".format(var[2], var[1]))
            raise e
        # get the same bins and normalization for the pT ranges
        th1SmoothRange(hist, 2, 0., 1.)
        hist_rebin = ROOT.TH1D(hist.GetName() + "_rebin", "", len(orig_bins) - 1, orig_bins)
        hist_rebin.SetDirectory(0)
        ratio = hist.GetBinWidth(1) / nominal.GetBinWidth(1)
        for i_orig,x in enumerate(orig_bins):
            i_var = hist.GetXaxis().FindBin(x)
            n_var = hist.GetBinContent(i_var)
            hist_rebin.SetBinContent(i_orig + 1, n_var / ratio)
        variations.append((var[0], hist_rebin))
        tf.Close()

    drawVariations(plot["name"], nominal, variations, plot["title"], options.output, logy=plot.get("log", False), nominalName=plot.get("nominalName", None), norm=plot.get("norm", False), ratio_range=plot.get("ratio-range", None), smooth=plot.get("smooth", 0), nom_to_density=plot.get("nom_to_density", False), var_to_density=plot.get("var_to_density", False), ratio_style=plot.get("ratio-style", "histL"), leg_pos=plot.get("leg-pos", "l"))




#### debug: smooth vs. raw weights
for leg,gr,out in [
    ("B-L CP5 default to B-L CP5 central", "fragCP5BL", "weights_BL_central.pdf"),
    ("B-L CP5 default to B-L CP5 up", "fragCP5BLup", "weights_BL_up.pdf"),
    ("B-L CP5 default to B-L CP5 down", "fragCP5BLdown", "weights_BL_down.pdf"),
    ("B-L CP5 default to Peterson CP5 central", "fragCP5Peterson", "weights_peterson_central.pdf"),
    ("B-L CP5 default to Peterson CP5 up", "fragCP5Petersonup", "weights_peterson_up.pdf"),
    ("B-L CP5 default to Peterson CP5 down", "fragCP5Petersondown", "weights_peterson_down.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 central", "fragCUETP8M2T4BL", "weights_BL_cuetp8m2t4_central.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 central", "fragCUETP8M2T4BLLHC", "weights_BL_cuetp8m2t4_top-18-012_central.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 up", "fragCUETP8M2T4BLLHCup", "weights_BL_cuetp8m2t4_top-18-012_up.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 down", "fragCUETP8M2T4BLLHCdown", "weights_BL_cuetp8m2t4_top-18-012_down.pdf"),
                  ]:
    tf = ROOT.TFile.Open(options.input + "/bfragweights.root")
    notSmooth = tf.Get(gr)
    smooth = tf.Get(gr + "_smooth")
    tf.Close()
    c = ROOT.TCanvas("c", "c")
    
    c.SetTopMargin(0.05)
    c.SetLeftMargin(0.1)
    c.SetRightMargin(0.05)
    c.SetBottomMargin(0.1)
    c.SetTickx(1)

    notSmooth.SetMarkerColor(ROOT.kBlue)
    notSmooth.GetYaxis().SetLabelSize(0.03)
    notSmooth.GetYaxis().SetTitleSize(0.03)
    notSmooth.GetYaxis().SetTitleOffset(1.7)
    notSmooth.GetYaxis().SetTitle("Weight")
    notSmooth.GetXaxis().SetLabelSize(0.03)
    notSmooth.GetXaxis().SetTitleSize(0.03)
    notSmooth.GetXaxis().SetLabelOffset(0.02)
    notSmooth.GetXaxis().SetTitleOffset(1.5)
    notSmooth.GetXaxis().SetRangeUser(0, 2)
    notSmooth.GetXaxis().SetTitle("x_{b} = p_{T}(B)/p_{T}(jet)")

    smooth.SetLineWidth(3)

    notSmooth.Draw("AP0")
    smooth.Draw("Lsame")

    text = ROOT.TLatex(0.1, 0.96, leg)
    text.SetNDC(True)
    text.SetTextFont(40)
    text.SetTextSize(0.03)
    text.Draw("same")

    c.SaveAs(os.path.join(options.output, out))



### debug: smooth in pT bins
for leg,gr,out in [
    ("B-L CP5 default to B-L CP5 central", "fragCP5BL", "weights_pT_BL_central.pdf"),
    ("B-L CP5 default to B-L CP5 up", "fragCP5BLup", "weights_pT_BL_up.pdf"),
    ("B-L CP5 default to B-L CP5 down", "fragCP5BLdown", "weights_pT_BL_down.pdf"),
    ("B-L CP5 default to Peterson CP5 central", "fragCP5Peterson", "weights_pT_peterson_central.pdf"),
    ("B-L CP5 default to Peterson CP5 up", "fragCP5Petersonup", "weights_pT_peterson_up.pdf"),
    ("B-L CP5 default to Peterson CP5 down", "fragCP5Petersondown", "weights_pT_peterson_down.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 central", "fragCUETP8M2T4BL", "weights_pT_BL_cuetp8m2t4_central.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 central", "fragCUETP8M2T4BLLHC", "weights_pT_BL_cuetp8m2t4_top-18-012_central.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 up", "fragCUETP8M2T4BLLHCup", "weights_pT_BL_cuetp8m2t4_top-18-012_up.pdf"),
    ("B-L CP5 default to B-L CUETP8M2T4 TOP-18-012 down", "fragCUETP8M2T4BLLHCdown", "weights_pT_BL_cuetp8m2t4_top-18-012_down.pdf"),
                  ]:

    c = ROOT.TCanvas("c", "c")
    
    c.SetTopMargin(0.05)
    c.SetLeftMargin(0.1)
    c.SetRightMargin(0.05)
    c.SetBottomMargin(0.1)
    c.SetTickx(1)
    
    l = ROOT.TLegend(0.72, 0.6, 0.96, 0.92)
    l.SetTextFont(42)
    l.SetFillColor(ROOT.kWhite)
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    l.SetTextSize(0.023)
    
    tf = ROOT.TFile.Open(options.input + "/bfragweights.root")
    nominal = tf.Get(gr + "_smooth")
    l.AddEntry(nominal, "averaged")
    tf.Close()

    tf = ROOT.TFile.Open(options.input + "/bfragweights_vs_pt_debug.root")
    for ipT,pT in enumerate(pTranges):
        graph = tf.Get(gr + "_" + pT + "_smooth")
        
        l.AddEntry(graph, pT)

        graph.SetLineColor(ROOT.TColor.GetColor(colors[ipT+1]))
        graph.SetLineWidth(2)
        if ipT == 0:
            graph.GetYaxis().SetLabelSize(0.03)
            graph.GetYaxis().SetTitleSize(0.03)
            graph.GetYaxis().SetTitleOffset(1.7)
            graph.GetYaxis().SetTitle("Weight")
            graph.GetXaxis().SetLabelSize(0.03)
            graph.GetXaxis().SetTitleSize(0.03)
            graph.GetXaxis().SetLabelOffset(0.02)
            graph.GetXaxis().SetTitleOffset(1.5)
            graph.GetXaxis().SetRangeUser(0, 1)
            graph.GetYaxis().SetRangeUser(0, 3)
            graph.GetXaxis().SetTitle("x_{b} = p_{T}(B)/p_{T}(jet)")

            graph.Draw("AL")
        else:
            graph.Draw("Lsame")
        
    tf.Close()

    nominal.SetLineColor(nominal_color)
    nominal.SetLineWidth(3)
    nominal.SetLineStyle(2)
    nominal.Draw("Lsame")

    text = ROOT.TLatex(0.1, 0.96, leg)
    text.SetNDC(True)
    text.SetTextFont(40)
    text.SetTextSize(0.03)
    text.Draw("same")
    
    l.Draw("same")

    c.SaveAs(os.path.join(options.output, out))



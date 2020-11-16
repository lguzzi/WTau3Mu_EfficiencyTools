import ROOT
import numpy
from collections import OrderedDict
import json
from itertools import product
import sys, os

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--data', required = True, type = str, help = 'data efficiencies json')
parser.add_argument('--mc'  , required = True, type = str, help = 'mc efficiencies json')
parser.add_argument('--sf'  , required = True, type = str, help = 'sf json path')
parser.add_argument('--out' , required = True, type = str, help = 'sf output dir')
parser.add_argument('--label', required = True, type = str, help = 'label')
parser.add_argument('--visualize', action = 'store_true')
args = parser.parse_args()

ROOT.gROOT.SetBatch(not args.visualize)

def grapher(x, y, yl, yh, col):
  xv = numpy.array([0.5*float(xx.split('_')[1]) + 0.5*float(xx.split('_')[0]) for xx in x], dtype = numpy.single)
  xe = numpy.array([0.5*float(xx.split('_')[1]) - 0.5*float(xx.split('_')[0]) for xx in x], dtype = numpy.single)
  yv = numpy.array(y , dtype = numpy.single)
  yel = numpy.array(yl, dtype = numpy.single)
  yeh = numpy.array(yh, dtype = numpy.single)

  g = ROOT.TGraphAsymmErrors(len(xv), xv, yv, xe, xe, yel, yeh)
  g.GetYaxis().SetRangeUser(0, 1.1)
  g.SetMarkerStyle(20)
  g.SetMarkerColor(col)
  g.SetLineColor(col)
  return g

def printRatioGraphs (daGraph, mcGraph, sfGraph, varName, xmin, xmax, printDir = None, label = '', logx = False):
  ## define some ranges
  yEffHigh = 1.3*max (  ROOT.TMath.MaxElement(daGraph.GetN(), daGraph.GetY()),
                        ROOT.TMath.MaxElement(mcGraph.GetN(), mcGraph.GetY()))
  yEffLow  = 0

  ySFHigh = 1.1*ROOT.TMath.MaxElement(sfGraph.GetN(), sfGraph.GetY())
  ySFHigh = ySFHigh if ySFHigh < 7 else 7
  ySFLow  = 0#0.8*ROOT.TMath.MinElement(sfGraph.GetN(), sfGraph.GetY())

  ## create support histos
  supportEff = ROOT.TH1F("suppE", "", 1, xmin, xmax)
  supportRat = ROOT.TH1F("suppR", "", 1, xmin, xmax)

  ## create the legend
  legPad = ROOT.TLegend(0.7, 0.55, 0.85, 0.45)
  legPad.AddEntry(daGraph, "Data", "lp")
  legPad.AddEntry(mcGraph, "MC"  , "lp")

  ## set up the gaphs
  multiG = ROOT.TMultiGraph()
  multiG.SetTitle("SFs - %s muon ID; %s; efficiency" % (varName, varName))
  multiG.Add(daGraph)
  multiG.Add(mcGraph)
  multiG.SetMinimum(yEffLow)
  multiG.SetMaximum(yEffHigh)
  mcGraph.SetLineColor(ROOT.kBlue)
  daGraph.SetLineColor(ROOT.kRed)
  mcGraph.SetMarkerStyle(20)
  daGraph.SetMarkerStyle(22)
  mcGraph.SetMarkerColor(ROOT.kBlue)
  daGraph.SetMarkerColor(ROOT.kRed)

  ## create the SF graph
  sfGraph.SetMarkerColor(ROOT.kBlack)
  sfGraph.SetLineColor(ROOT.kBlack)
  sfGraph.SetMarkerStyle(8)    
  sfGraph.SetFillStyle(3004)
  sfGraph.SetFillColor(ROOT.kBlack)

  outCan = ROOT.TCanvas("outCan%s" % varName, "", 700, 1000)
  outCan.SetTitle("SFs for %s binning  -  %s muonID" %(varName, varName))
  outCan.Divide(1, 2)
  ## set the pads
  outCan.GetListOfPrimitives()[0].SetPad('effPad%s'   % varName, 'effPad'  , 0., 0.30, 1., 1., 0, 0)
  outCan.GetListOfPrimitives()[1].SetPad('ratioPad%s' % varName, 'ratioPad', 0., 0.32, 1., .0, 0, 0)
  outCan.GetListOfPrimitives()[0].SetLogx(logx)
  outCan.GetListOfPrimitives()[1].SetLogx(logx)

  outCan.GetListOfPrimitives()[0].SetGridy(True)
  outCan.GetListOfPrimitives()[1].SetGridy(True)
  outCan.GetListOfPrimitives()[0].SetGridx(True)
  outCan.GetListOfPrimitives()[1].SetGridx(True)

  outCan.GetListOfPrimitives()[0].SetBottomMargin(0.12)
  outCan.GetListOfPrimitives()[1].SetTopMargin(0.12)
  
  ## draw the results
  outCan.cd(1)
  supportEff.Draw()
  multiG.Draw("same p")
  multiG.GetXaxis().SetLimits(xmin, xmax)
  multiG.GetXaxis().SetTitleOffset( 1.3*multiG.GetXaxis().GetTitleOffset())
  legPad.Draw("same")

  outCan.cd(2)

  multiR = ROOT.TMultiGraph()
  multiR.SetTitle("; ; data / MC")
  multiR.Add(sfGraph)
  multiR.GetXaxis().SetLimits(xmin, xmax)
  multiR.SetMaximum(ySFHigh)
  multiR.SetMinimum(ySFLow )
  sfGraph.GetXaxis().SetLimits(xmin, xmax)

  #supportRat.Draw()
  multiR.Draw("APLE3")

  outCan.Modified()
  outCan.Update()

  line = ROOT.TLine(xmin, 1, xmax, 1)
  line.SetLineColor(ROOT.kRed)
  line.SetLineWidth(1)
  line.Draw("SAME")

  ## draw on the ratio pad
  if not printDir is None:
    if not os.path.exists(printDir):
      os.makedirs(printDir)
    outCan.Print("%s/SFs_%s.pdf" % (printDir, label), "pdf")

  return 

if __name__ == '__main__':
  da_json = json.load(open(args.data, 'r'), object_pairs_hook = OrderedDict)
  mc_json = json.load(open(args.mc  , 'r'), object_pairs_hook = OrderedDict)
  sf_json = json.load(open(args.sf  , 'r'), object_pairs_hook = OrderedDict)

  iterator = lambda jsn: [(ee, [(pp, jsn['abseta'][ee]['pt'][pp]) for pp in jsn['abseta'][ee]['pt'].keys()]) for ee in jsn['abseta'].keys()]

  da_graphs = [(it[0], grapher(x = [x[0] for x in it[1]], y = [x[1]['value'] for x in it[1]], yl = [x[1]['error_low'] for x in it[1]], yh = [x[1]['error_high'] for x in it[1]], col = ROOT.kBlue )) for it in iterator(da_json)]
  mc_graphs = [(it[0], grapher(x = [x[0] for x in it[1]], y = [x[1]['value'] for x in it[1]], yl = [x[1]['error_low'] for x in it[1]], yh = [x[1]['error_high'] for x in it[1]], col = ROOT.kRed  )) for it in iterator(mc_json)]
  sf_graphs = [(it[0], grapher(x = [x[0] for x in it[1]], y = [x[1]['value'] for x in it[1]], yl = [x[1]['error'] for x in it[1]], yh = [x[1]['error'] for x in it[1]], col = ROOT.kBlack)) for it in iterator(sf_json)]

  multigraphs = [(b1, (g1, g2, g3)) for b1, g1 in da_graphs for b2, g2 in mc_graphs for b3, g3 in sf_graphs if b1 == b2 == b3]

  for bb, (da, mc, sf) in multigraphs:
    printRatioGraphs(daGraph = da, mcGraph = mc, sfGraph = sf, varName = 'pt', xmin = 0, xmax = 100, printDir = '{}/pdf/{}'.format(args.out, args.label), logx = True, label = bb)
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
ROOT.gStyle.SetOptStat(0)

def to_histo(points, title):
  y_bins = [pp[0]    for pp in points]
  x_bins = [pp[0] for pp in points[0][1]]

  histo = ROOT.TH2F(title, '', len(x_bins), 0, len(x_bins), len(y_bins), 0, len(y_bins))
  for bb in range(histo.GetNbinsX()): histo.GetXaxis().SetBinLabel(bb+1, x_bins[bb])
  for bb in range(histo.GetNbinsY()): histo.GetYaxis().SetBinLabel(bb+1, y_bins[bb])
  import pdb; pdb.set_trace()

  for (ix, xx), (iy, yy) in product(enumerate(x_bins), enumerate(y_bins)):
    histo.SetBinContent(ix+1, , iy+1, )

if __name__ == '__main__':
  da_json = json.load(open(args.data, 'r'), object_pairs_hook = OrderedDict)
  mc_json = json.load(open(args.mc  , 'r'), object_pairs_hook = OrderedDict)
  sf_json = json.load(open(args.sf  , 'r'), object_pairs_hook = OrderedDict)

  iterator = lambda jsn: [(ee, [(pp, jsn['abseta'][ee]['pt'][pp]) for pp in jsn['abseta'][ee]['pt'].keys()]) for ee in jsn['abseta'].keys()]

  da_hist = to_histo([jj for jj in iterator(da_json)], title = 'data efficiencies {}'.format(args.label))
  mc_hist = to_histo([jj for jj in iterator(mc_json)], title = 'mc efficiencies {}'.format(args.label))
  sf_hist = to_histo([jj for jj in iterator(sf_json)], title = 'scale factors {}'.format(args.label))

  can = ROOT.TCanvas()
  da_hist.Draw('COLZ2')
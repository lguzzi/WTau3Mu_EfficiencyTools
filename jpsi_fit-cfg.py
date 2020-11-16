from __future__ import print_function
import ROOT
from libs.bin_cls import Bin
from libs.funcs   import binned, extend
from collections import OrderedDict
from itertools import product
import glob
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--muonid'   , required = True , type = str, help = 'muon ID under test')
parser.add_argument('--sample'   , required = True , type = str, help = 'sample under test')
parser.add_argument('--version'  , default  = ''   , type = str, help = 'fit version (label)')
parser.add_argument('--n_threads', default  = 1    , type = int, help = 'number of threads')
parser.add_argument('--visualize', action = 'store_true', help = 'won\'t run in batch mode')
args = parser.parse_args()

ROOT.gROOT.SetBatch(not args.visualize)
if args.n_threads > 1:
  ROOT.ROOT.EnableImplicitMT(args.n_threads)

OUTDIR = 'Efficiencies{}'.format(args.version)

if __name__ == '__main__':
  input_files = ROOT.std.vector('std::string')()
  json_dict = OrderedDict()

  files = {
    'mc'   : glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/MC_Jpsi_pt8GeV/*.root'),
    '2017B': glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/Run2017B/*.root'),
    '2017C': glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/Run2017B/*.root'),
    '2017D': glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/Run2017B/*.root'),
    '2017E': glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/Run2017B/*.root'),
    '2017F': glob.glob('/eos/cms/store/group/phys_muon/TagAndProbe/ULRereco/2017/102X/Jpsi/12Jun2020/Mu8Mu17Mu20/Run2017B/*.root'),
  } ; files['2017all'] = [jj for key, paths in files.items() for jj in paths if not key == 'mc']

  for file in files[args.sample]:
    input_files.push_back(str(file))

  dataframe = ROOT.RDataFrame('tpTree/fitter_tree', input_files)

  from libs.models import cbgauss_sum, expo_pass, expo_fail, crystalball, gaussian, doublegauss
  wspace = ROOT.RooWorkspace('wspace')  
  getattr(wspace, 'import')(crystalball.Clone('signal'))
  getattr(wspace, 'import')(expo_pass.Clone('backgroundPass'))
  getattr(wspace, 'import')(expo_fail.Clone('backgroundFail'))
  extend(wspace)

  binned_variables = OrderedDict()
  #binned_variables['abseta'] = binned([0, 0.9, 1.2, 2.1, 2.4])
  binned_variables['abseta'] = binned([0, 2.4])
  binned_variables['pt' ]    = binned([2, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.5, 5, 6, 8, 10, 15, 20, 25, 30, 40, 50, 9999])#, 60, 120, 200, 300, 500, 700, 1200])

  tight2016 = ('tight2016', 'Glb == 1 && PF == 1 && glbChi2 < 10 && glbValidMuHits > 0 && numberOfMatchedStations > 1 && dB < 0.2 && dzPV < 0.5 && tkValidPixelHits > 0 && tkTrackerLay > 5')
  soft2016  = ('soft2016' , 'TMOST == 1 && Track_HP == 1 && tkTrackerLay > 5 && tkPixelLay > 0 && abs(dzPV) < 20. && abs(dB) < 0.3')

  denominator = ' && '.join([
    'tag_pt > 8',
    'pt > 2',
    'abseta > 0 && abseta < 2.4',
    
    '(tag_Mu8 || tag_Mu17 || tag_Mu20)',
    'pair_dz < 0.5',
    'pair_drM1 >= 0.3', 
  ])

  dataframe = dataframe.Define(*tight2016).Define(*soft2016)
  dataframe = dataframe.Filter(denominator)
  numerator = {
    'tight2016' : 'tight2016',
    'medium2016': 'Medium2016',
    'loose'     : 'Loose',
    'soft2016'  : 'soft2016',

    'mediumNOTtight': 'Medium2016 && !tight2016',
    'looseNOTmedium': 'Loose && !Medium2016 && !tight2016',
    'softNOTloose'  : 'soft2016 && !Loose && !Medium2016 && !tight2016',
  }

  ## convert all the possible combination of binned_variables in a smart structure
  bin_list = [[(a, b) for b in binned_variables[a]]  for a in binned_variables.keys()]
  bin_list = [[('{K}/{LO}_{UP}'.format(K = k, LO = x[0], UP = x[1]), '{K} >= {LO} && {K} < {UP}'.format(K = k, LO = x[0], UP = x[1])) for k, x in X] for X in bin_list]
  bin_list = [x for x in product(*[X for X in bin_list])]
  bin_list = [('/'.join([x[0] for x in X]), ' && '.join([x[1] for x in X])) for X in bin_list]
  #for bb in bin_list: bb[1] = '({}) && ({})'.format(denominator, bb[1])

  bins = [
    Bin(den = den, num = numerator[args.muonid], tdir = tdir, dataframe = dataframe, workspace = wspace.Clone(), isMC = args.sample == 'mc')
      for tdir, den in bin_list
  ]

  print ('[INFO] loading histograms')
  for bb in bins:
    bb.load_histograms()

  for bb in bins:
    bb.run_fit(out_dir = '{}/{}_{}'.format(OUTDIR, args.sample, args.muonid), json_dict = json_dict)

  print ('[INFO] all done. RDF was read', getattr(dataframe, 'GetNRuns', lambda: '[RDF.GetNRuns() not available in this ROOT version]')(), 'time(s)')
  json.dump(json_dict, open('{}/{}_{}.json'.format(OUTDIR, args.sample, args.muonid), 'w'), indent = 4)
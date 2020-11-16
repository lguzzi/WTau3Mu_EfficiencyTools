import json
from collections import OrderedDict
from uncertainties import ufloat

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--data', required = True, type = str, help = 'data efficiencies json')
parser.add_argument('--mc'  , required = True, type = str, help = 'mc efficiencies json')
parser.add_argument('--out' , required = True, type = str, help = 'output json file path')
args = parser.parse_args()

def read_json(da, mc, sf):
  if 'value' in da.keys():
    da_eff = ufloat(da['value'], da['error'])
    mc_eff = ufloat(mc['value'], mc['error'])
    sf_obj = da_eff / mc_eff if mc_eff.nominal_value != 0 else ufloat(0, 1)

    sf['value'] = sf_obj.nominal_value
    sf['error'] = sf_obj.std_dev

    return True
  
  for kk in da.keys():
    if not kk in sf.keys():
      sf[kk] = OrderedDict()
    if read_json(da = da[kk], mc = mc[kk], sf = sf[kk]):
      continue

if __name__ == '__main__':
  data_json = json.load(open(args.data, 'r'), object_pairs_hook = OrderedDict)
  mc_json   = json.load(open(args.mc  , 'r'), object_pairs_hook = OrderedDict)

  sf_json   = OrderedDict()

  read_json(da = data_json, mc = mc_json, sf = sf_json)
  json.dump(sf_json, open(args.out, 'w'), indent = 4)
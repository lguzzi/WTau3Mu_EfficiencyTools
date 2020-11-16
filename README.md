# WTau3Mu_EfficiencyTools

Bugs may be present.   
Use this tools to evaluate num-over-den efficiencies.
Having defined a list of bins, the tool runs a simultaneous fit on passing and failing events given some selections to evaluate the 'efficiency' parameter from the fit.  
Fits are run on TH1F histograms, which are loaded from a RDataFrame.

## Requirements

- ROOT >= 6.14

## How to

The main executable should be a python cfg file (ex. [here](https://github.com/lguzzi/WTau3Mu_EfficiencyTools/blob/master/jpsi_fit-cfg.py)).
The cfg file shoul build a list of bins; the efficiency is calculated for each bin.  
Bins are defined usign the [Bin class](https://github.com/lguzzi/WTau3Mu_EfficiencyTools/blob/master/libs/bin_cls.py), which requires:

  - a numerator string (e.g. "var1 > x && var 2 > y")
  - a denominator string, including the bin selection string
  - a dataframe (RDataFrame)
  - a workspace (RooWorkspace)
 
 The dataframe contains all the information used to run the fit, namely the variables which define the numerator and denominator, and the fit variable.  
 The workspace should contain three functions with the following names:
  
  - backgroundPass
  - backgroundFail
  - signal
 
Once the dataframe is defined inside the python cfg script, the [extend()](https://github.com/lguzzi/WTau3Mu_EfficiencyTools/blob/master/libs/funcs.py#L6) function can be called to configure the model (i.e. to create workspace structure needed to run the simultaneous fit).  
Each instance of the Bin class contains a RDF pointer to the histogram which will be fitted. To load these histograms you should call the [load_histogram()](https://github.com/lguzzi/WTau3Mu_EfficiencyTools/blob/master/libs/bin_cls.py#L30) function for each bin (after all bins instances have been created). This will take a few minutes.
Once histograms are loaded into memory, you can call the [run_fit()](https://github.com/lguzzi/WTau3Mu_EfficiencyTools/blob/master/libs/bin_cls.py#L43) function for each bin. It requires the following arguments:

  - out_dir: output directory (where to save the fit canvases)
  - json_dict (a json instance to save the results in a json format)
  
Both can be omitted, in which case nothing is saved.

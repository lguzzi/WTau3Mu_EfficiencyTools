from __future__ import print_function
import ROOT
import os
from collections import OrderedDict

class Bin:
  def __init__(self, den, num, tdir, dataframe, workspace, var = 'mass', poi = 'efficiency', isMC = False):
    self.var  = var
    self.den  = '('+den+')'
    self.num  = '('+num+')'
    self.tdir = tdir
    self.dfr  = dataframe

    self.wspace = workspace
    model = (self.wspace.var(self.var).GetName(), self.wspace.var(self.var).GetTitle(), self.wspace.var(self.var).getBins(), self.wspace.var(self.var).getRange().first, self.wspace.var(self.var).getRange().second)

    histo_model = (model, self.var)# if not isMC else (model, self.var, 'weight')
    self.ptr_tot = dataframe.Filter(self.den                              , 'total').Histo1D(*histo_model)
    self.ptr_pas = dataframe.Filter(' && '.join([self.den,     self.num]) , 'pass' ).Histo1D(*histo_model)
    self.ptr_fai = dataframe.Filter(' && '.join([self.den, '!'+self.num]) , 'fail' ).Histo1D(*histo_model)

    self.cat = ROOT.RooCategory('cat', 'fit categories')
    self.cat.defineType('passed')
    self.cat.defineType('failed')
    
    self.fit_model = ROOT.RooSimultaneous('model', 'fit model', self.cat)
    self.fit_model.addPdf(self.wspace.pdf('pass_pdf'), 'passed')
    self.fit_model.addPdf(self.wspace.pdf('fail_pdf'), 'failed')   

  def load_histograms(self):
    hst_pas = ROOT.RooDataHist('', '', ROOT.RooArgList(self.wspace.var('mass')), self.ptr_pas.GetValue())
    hst_fai = ROOT.RooDataHist('', '', ROOT.RooArgList(self.wspace.var('mass')), self.ptr_fai.GetValue())
    hst_tot = ROOT.RooDataHist('', '', ROOT.RooArgList(self.wspace.var('mass')), self.ptr_tot.GetValue())

    self.data = ROOT.RooDataHist('data', 'events for {}'.format(self.tdir), 
                                ROOT.RooArgSet(self.wspace.var(self.var)),
                                ROOT.RooFit.Index(self.cat), 
                                ROOT.RooFit.Import('passed', hst_pas),  
                                ROOT.RooFit.Import('failed', hst_fai),
                                #ROOT.RooFit.Import('total' , totl_set)
    )
    
  def run_fit(self, out_dir = None, json_dict = None):
    self.fit_results = self.fit_model.fitTo(self.data, ROOT.RooFit.Extended(True), ROOT.RooFit.Save(True), ROOT.RooFit.Minos(True))
    
    for jj in range(5):
      if self.fit_results.covQual() == 3: break
      self.fit_results = self.fit_model.fitTo(self.data, ROOT.RooFit.Extended(True), ROOT.RooFit.Save(True), ROOT.RooFit.Minos(True))
      
    frame_pas = self.wspace.var('mass').frame(ROOT.RooFit.Title("Passing events"))
    frame_fai = self.wspace.var('mass').frame(ROOT.RooFit.Title("Failing events"))
    frame_tot = self.wspace.var('mass').frame(ROOT.RooFit.Title("Total events"  ))

    self.can = ROOT.TCanvas()
    self.can.Divide(2, 2)
    
    ## see https://root-forum.cern.ch/t/roofit-simultaneous-fit-problem/21870/2
    self.data.plotOn(frame_pas, ROOT.RooFit.Cut("cat==cat::passed"))
    self.data.plotOn(frame_fai, ROOT.RooFit.Cut("cat==cat::failed"))
    self.data.plotOn(frame_tot)

    self.fit_model.plotOn(frame_pas, ROOT.RooFit.Slice(self.cat, 'passed'), ROOT.RooFit.ProjWData(self.data), ROOT.RooFit.LineColor(ROOT.kGreen))
    self.fit_model.plotOn(frame_fai, ROOT.RooFit.Slice(self.cat, 'failed'), ROOT.RooFit.ProjWData(self.data), ROOT.RooFit.LineColor(ROOT.kRed)  )
    self.fit_model.plotOn(frame_tot,                                        ROOT.RooFit.ProjWData(self.data), ROOT.RooFit.LineColor(ROOT.kBlue) )

    self.fit_model.plotOn(frame_pas, ROOT.RooFit.Slice(self.cat, 'passed'), ROOT.RooFit.ProjWData(self.data), ROOT.RooFit.LineColor(ROOT.kGreen), ROOT.RooFit.Components("backgroundPass"),  ROOT.RooFit.LineStyle(ROOT.kDashed))
    self.fit_model.plotOn(frame_fai, ROOT.RooFit.Slice(self.cat, 'failed'), ROOT.RooFit.ProjWData(self.data), ROOT.RooFit.LineColor(ROOT.kRed)  , ROOT.RooFit.Components("backgroundFail"),  ROOT.RooFit.LineStyle(ROOT.kDashed))

    fit_pars = ROOT.RooArgList(self.fit_model.getParameters(self.data))
    fit_pars = [fit_pars.at(pp) for pp in range(len(fit_pars))] 
    box = ROOT.TPaveText(0.1, 0.1, 0.9, 0.9)
    
    box.AddText('Fit status: {}'.format(self.fit_results.status()))
    box.AddText('Cov. Matrix quality: {}'.format(self.fit_results.covQual()))
    box.AddText('-'*40)
    for pp in fit_pars:
        box.AddText('{} {} #pm {} {}'.format(pp.GetName(), round(pp.getVal(), 3), round(pp.getError(), 3), pp.getUnit()))

    self.efficiency = self.wspace.var('efficiency').getVal()
    self.eff_errors = -self.wspace.var('efficiency').getErrorLo(), self.wspace.var('efficiency').getErrorHi()
    self.eff_error  = self.wspace.var('efficiency').getError() 

    self.can.cd(1) ; frame_pas.Draw()
    self.can.cd(2) ; frame_fai.Draw()
    self.can.cd(3) ; frame_tot.Draw()
    self.can.cd(4) ; box.Draw()
    
    if not out_dir is None:
      self.out = out_dir
      self.pdf = '/'.join([self.out, 'pdf'])

      if not os.path.exists(self.pdf):
        os.makedirs(self.pdf)
      
      self.can.SaveAs('{}/{}.pdf'.format(self.pdf, self.tdir.replace('/', '_')), 'pdf')
    
    if not json_dict is None:
      here = json_dict
      for td in self.tdir.split('/'):
        if not td in here.keys():
          here[td] = OrderedDict()
        here = here[td]
      here['value'] = self.efficiency
      here['error_low' ] = self.eff_errors[0]
      here['error_high'] = self.eff_errors[1]
      here['error']      = self.eff_error
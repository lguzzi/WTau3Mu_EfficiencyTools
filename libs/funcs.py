import ROOT

def binned(bin_edges):
  return [(lo, up) for lo, up in zip(bin_edges[:-1], bin_edges[1:])]

def extend(workspace):
  getattr(workspace, 'import')( ROOT.RooRealVar('efficiency', 'selection efficiency'    , 0.e+0, 1.e+0, ''))
  workspace.var('efficiency').setVal(0.)
  getattr(workspace, 'import')( ROOT.RooRealVar('nsig_totl' , 'number of signal events' , 0e+0 , 1e+6 , ''))
  getattr(workspace, 'import')( ROOT.RooRealVar('nbkg_pass' , 'number of passing background events' , 0e+0 , 1e+6 , ''))
  getattr(workspace, 'import')( ROOT.RooRealVar('nbkg_fail' , 'number of failing background events' , 0e+0 , 1e+6 , ''))
  
  getattr(workspace, 'import')( ROOT.RooFormulaVar('nsig_pass', '', '@0*@1'      , ROOT.RooArgList(workspace.var('efficiency'), workspace.var('nsig_totl'))))
  getattr(workspace, 'import')( ROOT.RooFormulaVar('nsig_fail', '', '(1.-@0)*@1' , ROOT.RooArgList(workspace.var('efficiency'), workspace.var('nsig_totl'))))

  getattr(workspace, 'import')( ROOT.RooAddPdf('pass_pdf', 'passing events pdf', 
                                ROOT.RooArgList(workspace.pdf('signal') , workspace.pdf('backgroundPass' )), 
                                ROOT.RooArgList(workspace.obj('nsig_pass'), workspace.var('nbkg_pass')))
  )
  getattr(workspace, 'import')( ROOT.RooAddPdf('fail_pdf', 'failing events pdf', 
                                ROOT.RooArgList(workspace.pdf('signal') , workspace.pdf('backgroundFail' )), 
                                ROOT.RooArgList(workspace.obj('nsig_fail'), workspace.var('nbkg_fail')))
  )
  getattr(workspace, 'import')( ROOT.RooAddPdf('totl_pdf', 'total events pdf',
                                ROOT.RooArgList(workspace.pdf('pass_pdf'), workspace.pdf('fail_pdf')))
  )
  
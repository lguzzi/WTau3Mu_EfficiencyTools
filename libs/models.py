import ROOT

## variables
mass        = ROOT.RooRealVar('mass'      , 'tag-probe mass'          , 2.8, 3.4, 'GeV')
mean        = ROOT.RooRealVar('mean'      , 'J/#Psi mass value'       , 3.05, 3.15, 'GeV')
sigma_CB    = ROOT.RooRealVar('sigma_CB'  , 'CrystalBall width'       , 0.05, 0.02, 0.1, 'GeV')
alpha_CB    = ROOT.RooRealVar('alpha_CB'  , 'CrystalBall alpha'       , 3., 1, 10)
n_CB        = ROOT.RooRealVar('n_CB'      , 'CrystalBall n'           , 1., 5, 1000.)
sigma_G     = ROOT.RooRealVar('sigma_G'   , 'Gaussian width'          , 0.05, 0.02, 0.1, 'GeV')
sigma_G1    = ROOT.RooRealVar('sigma_G1'  , 'Gaussian1 width'         , 0.05, 0.02, 0.1, 'GeV')
sigma_G2    = ROOT.RooRealVar('sigma_G2'  , 'Gaussian2 width'         , 0.05, 0.02, 0.1, 'GeV')
slope_pass  = ROOT.RooRealVar('slope_pass', 'Background slope (pass)' , 0, -10, 10)
slope_fail  = ROOT.RooRealVar('slope_fail', 'Background slope (fail)' , 0, -10, 10)
gauss_frac  = ROOT.RooRealVar('gauss_frac', 'Gaussian fraction'       , 0.5, 0, 1)
gauss1_frac = ROOT.RooRealVar('gaus1_frac', 'Gaussian1 fraction'      , 0.5, 0, 1)

mass.setBins(60)

## models
gaussian    = ROOT.RooGaussian   ('gaussian'      , 'Gaussian function'       , mass, mean, sigma_G)
crystalball = ROOT.RooCBShape    ('crystallball'  , 'CrystallBall function'   , mass, mean, sigma_CB, alpha_CB, n_CB)
cbgauss_sum = ROOT.RooAddPdf     ('cbgauss_sum'   , 'Gaussian + CrystallBall' , ROOT.RooArgList(gaussian, crystalball), ROOT.RooArgList(gauss_frac))

expo_pass   = ROOT.RooExponential('backgroundPass', 'Background (pass)'       , mass, slope_pass)
expo_fail   = ROOT.RooExponential('backgroundFail', 'Background (fail)'       , mass, slope_fail)

gaussian1   = ROOT.RooGaussian   ('gaussian'      , 'Gaussian1 function'      , mass, mean, sigma_G1)
gaussian2   = ROOT.RooGaussian   ('gaussian'      , 'Gaussian2 function'      , mass, mean, sigma_G2)
doublegauss = ROOT.RooAddPdf     ('doubelgauss'   , '2Gaussian'               , ROOT.RooArgList(gaussian1, gaussian2), ROOT.RooArgList(gauss1_frac))

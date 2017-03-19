import FWCore.ParameterSet.Config as cms

bfragProd = cms.EDProducer('BFragmentationProducer',
                           cfg = cms.FileInPath('TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights.root')
                           )

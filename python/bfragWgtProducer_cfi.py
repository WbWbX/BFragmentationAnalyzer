import FWCore.ParameterSet.Config as cms

bfragWgtProducer = cms.EDProducer('BFragmentationWeightProducer',
                                  cfg = cms.FileInPath('TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights.root')
                                  )

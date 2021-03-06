import FWCore.ParameterSet.Config as cms

bfragAnalysis = cms.EDAnalyzer("BFragmentationAnalyzer",
                               hadronList = cms.vint32(511,521,531,5122),
                               debug = cms.untracked.bool(False)
                               )

import FWCore.ParameterSet.Config as cms

bfragWgtProducer = cms.EDProducer('BFragmentationWeightProducer',
                                  src = cms.InputTag("particleLevel:jets"),
                                  br_weight_file = cms.FileInPath('TopQuarkAnalysis/BFragmentationAnalyzer/data/bdecayweights.root'),
                                  frag_weight_file = cms.FileInPath('TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights.root'),
                                  frag_weight_vs_pt_file = cms.FileInPath('TopQuarkAnalysis/BFragmentationAnalyzer/data/bfragweights_vs_pt.root'),
                                  br_weights = cms.vstring(["semilepbrup", "semilepbrdown"]),
                                  frag_weights = cms.vstring([]),
                                  frag_weights_vs_pt = cms.vstring([
                                        "fragCP5BL", # CP5, Bowler-Lund, tuned to LEP + up/down uncertainties
                                        "fragCP5BLdown",
                                        "fragCP5BLup",
                                        "fragCP5Peterson", # CP5, Peterson, tuned to LEP + up/down uncertainties
                                        "fragCP5Petersondown",
                                        "fragCP5Petersonup",
                                        "fragCUETP8M2T4BL", # CUETP8M2T4, Bowler-Lund, tuned to LEP (assuming Monash)
                                        "fragCUETP8M2T4BLdefault", # CUETP8M2T4, Bowler-Lund, Pythia8 default
                                        "fragCUETP8M2T4BLLHC", # CUETP8M2T4, Bowler-Lund, TOP-18-012 result + up/down uncertainties
                                        "fragCUETP8M2T4BLLHCdown",
                                        "fragCUETP8M2T4BLLHCup",
                                  ]),
                                  )

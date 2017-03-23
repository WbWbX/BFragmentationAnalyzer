import FWCore.ParameterSet.Config as cms

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')
options.register('inputFile', 
                 '/store/mc/RunIISummer16MiniAODv2/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/36CDAE89-B3BE-E611-B022-0025905B8604.root',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "input file to process"
                 )
options.parseArguments()

process = cms.Process("Analysis")

# global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '80X_mcRun2_asymptotic_2016_TrancheIV_v7')

#message logger
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = ''
process.MessageLogger.cerr.FwkReport.reportEvery = 1000


# set input to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFile),
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck') 
                            )


# pseudo-top
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.mergedGenParticles = cms.EDProducer("MergedGenParticleProducer",
                                            inputPruned = cms.InputTag("prunedGenParticles"),
                                            inputPacked = cms.InputTag("packedGenParticles"),
                                            )
from GeneratorInterface.RivetInterface.genParticles2HepMC_cfi import genParticles2HepMC
process.genParticles2HepMC = genParticles2HepMC.clone( genParticles = cms.InputTag("mergedGenParticles") )
process.load("TopQuarkAnalysis.TopEventProducers.producers.pseudoTop_cfi")
process.pseudoTop.leptonMinPt=cms.double(20)
process.pseudoTop.leptonMaxEta=cms.double(2.5)
process.pseudoTop.jetMaxEta=cms.double(5.0)

process.load('TopQuarkAnalysis.BFragmentationAnalyzer.bfragWgtProducer_cfi')

process.p = cms.Path(process.pseudoTop*process.bfragWgtProducer)


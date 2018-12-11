import FWCore.ParameterSet.Config as cms

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')
options.register('inputFile', 
                 '/store/mc/RunIISummer16MiniAODv3/ST_t-channel_antitop_4f_mtop1715_inclusiveDecays_13TeV-powhegV2-madspin-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v1/120000/16CEB785-3FE6-E811-AAE8-FA163E9D74F8.root',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "input file to process"
                 )
options.parseArguments()

process = cms.Process("Analysis")

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
process.load('GeneratorInterface.RivetInterface.genParticles2HepMC_cfi')
process.genParticles2HepMC.genParticles = cms.InputTag("mergedGenParticles")
process.genParticles2HepMC.genEventInfo = cms.InputTag("generator")
process.load("GeneratorInterface.RivetInterface.particleLevel_cfi")
process.particleLevel.excludeNeutrinosFromJetClustering = False

# b-frag weight producer
process.load('TopQuarkAnalysis.BFragmentationAnalyzer.bfragWgtProducer_cfi')

process.p = cms.Path(process.mergedGenParticles*process.genParticles2HepMC*process.particleLevel*process.bfragWgtProducer)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("bfragWgtProducer.root"),
    outputCommands = cms.untracked.vstring(
        "drop *",
        "keep *_bfragWgtProducer_*_*",
    ),
)
process.outPath = cms.EndPath(process.out)

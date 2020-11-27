import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing ('python')
options.register('frag', 
		 'BL', 
		 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
		 "Fragmentation formula to use: BL (Bowler-Lund) P (Peterson)")
options.register('param', 
		 0.855, 
		 VarParsing.multiplicity.singleton,
                 VarParsing.varType.float,
		 "StringZ:rFactB (BL) or StringZ:epsilonB (P)")
options.register('tune', 
		 'CP5', 
		 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Tune to use: CP5, CUETP8M1, CUETP8M2T4")
options.register('seed', 
		 123456,
		 VarParsing.multiplicity.singleton,
                 VarParsing.varType.int,
		 "Random seed for event generation")
options.parseArguments()
print(options.outputFile)

process = cms.Process('GEN')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13TeV2016Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Make sure the LHE generator uses a different seed!
process.RandomNumberGeneratorService.generator.initialSeed = options.seed
process.RandomNumberGeneratorService.externalLHEProducer.initialSeed = options.seed

# Input source -> running directly on LHEs
# process.source = cms.Source("PoolSource",
#     dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
#     fileNames = cms.untracked.vstring(
#         '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FEAE2677-EFD9-E411-B1C4-02163E00E966.root',
#     ),
#     inputCommands = cms.untracked.vstring('keep *',
#         'drop LHEXMLStringProduct_*_*_*'),
#     secondaryFileNames = cms.untracked.vstring()
# )

process.options = cms.untracked.PSet(
 wantSummary = cms.untracked.bool(True)
)

process.source = cms.Source("EmptySource")

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/GenProduction/python/TOP-RunIISummer19UL16wmLHEGEN-00004-fragment.py nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/powheg/V2/TT_hvq/TT_hdamp_NNPDF31_NNLO_dilepton.tgz'),
    nEvents = cms.untracked.uint32(options.maxEvents),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8CUEP8M2T4Settings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *

tune = options.tune.lower()
if tune == "cp5":
    tuneSettingsBlock = pythia8CP5SettingsBlock
    tuneSettings = 'pythia8CP5Settings'
elif tune == "cuep8m2t4":
    tuneSettingsBlock = pythia8CUEP8M2T4SettingsBlock
    tuneSettings = 'pythia8CUEP8M2T4Settings'
elif tune == "cuep8m1":
    tuneSettingsBlock = pythia8CUEP8M1SettingsBlock
    tuneSettings = 'pythia8CUEP8M1Settings'

process.generator = cms.EDFilter("Pythia8HadronizerFilter",
                                maxEventsToPrint = cms.untracked.int32(0),
                                pythiaPylistVerbosity = cms.untracked.int32(0),
                                filterEfficiency = cms.untracked.double(1.0),
                                pythiaHepMCVerbosity = cms.untracked.bool(False),
                                comEnergy = cms.double(13000.),
                                PythiaParameters = cms.PSet(
                                                            pythia8CommonSettingsBlock,
                                                            tuneSettingsBlock,
                                                            pythia8PowhegEmissionVetoSettingsBlock,
                                                            processParameters = cms.vstring(
                                                                    'POWHEG:nFinal = 2', ## Number of final state particles
                                                                    ## (BEFORE THE DECAYS) in the LHE
                                                                    ## other than emitted extra parton
                                                                    'TimeShower:mMaxGamma = 1.0',#cutting off lepton-pair production
                                                                    ##in the electromagnetic shower
                                                                    ##to not overlap with ttZ/gamma* samples
                                                                    '6:m0 = 172.5',    # top mass'
                                                                    ),
                                                            parameterSets = cms.vstring('pythia8CommonSettings',
                                                                                        tuneSettings,
                                                                                        'pythia8PowhegEmissionVetoSettings',
                                                                                        'processParameters'
                                                            )
                                )
)

if options.frag=='P':
	process.generator.PythiaParameters.processParameters.append('StringZ:usePetersonB = on')     
	process.generator.PythiaParameters.processParameters.append('StringZ:epsilonB = %f'%options.param)
if options.frag=='BL':
	process.generator.PythiaParameters.processParameters.append('StringZ:rFactB = %f'%options.param)

#pseudo-top config
from GeneratorInterface.RivetInterface.genParticles2HepMC_cfi import genParticles2HepMC
process.genParticles2HepMC = genParticles2HepMC.clone( genParticles = cms.InputTag("genParticles") )
process.load("GeneratorInterface.RivetInterface.particleLevel_cfi")
process.particleLevel.excludeNeutrinosFromJetClustering = False

#analysis config
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(options.outputFile)
                                   )
process.load('TopQuarkAnalysis.BFragmentationAnalyzer.bfragAnalysis_cfi')


# Path and EndPath definitions
process.ProductionFilterSequence = cms.Sequence(process.generator)
process.lhe_step = cms.Path(process.externalLHEProducer)
process.generation_step = cms.Path(process.pgen)
process.AnalysisSequence = cms.Path(process.genParticles2HepMC*process.particleLevel*process.bfragAnalysis)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.AnalysisSequence,process.genfiltersummary_step,process.endjob_step)

# filter all path with the production filter sequence
for path in process.paths:
    if path in ['lhe_step']: continue
    getattr(process,path)._seq = process.ProductionFilterSequence * getattr(process,path)._seq 

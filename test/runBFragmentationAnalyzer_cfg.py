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
options.parseArguments()

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
process.load('IOMC.EventVertexGenerators.VtxSmearedNominalCollision2015_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source("PoolSource",
    dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
    fileNames = cms.untracked.vstring( 
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E0E60B0A-EFD9-E411-944B-002590494C44.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E216B380-EFD9-E411-A286-003048FEC15C.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E41672D8-EFD9-E411-96A4-02163E00F2F9.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E41DFBBB-EFD9-E411-B7E3-02163E00F319.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E4F6FEEE-EED9-E411-ABA1-02163E00F4EF.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E612966B-EFD9-E411-A4DB-02163E00EAD0.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/E85BB4DA-EED9-E411-8FE2-02163E00E9BC.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/ECA3C5EB-EED9-E411-81A7-02163E00E838.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/EE20F46A-EFD9-E411-A1AF-02163E00E65E.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/EE6DBD4A-EFD9-E411-BEAA-02163E00EB31.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/F2BFB88A-EFD9-E411-9FF2-02163E012EA4.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/F632D740-EFD9-E411-BA6B-02163E00EB84.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/F64713DB-EFD9-E411-B6B7-02163E00E684.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/F88F27EB-EFD9-E411-A4B2-02163E00E6C5.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/F8E3A9AB-EFD9-E411-9266-002590494E94.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FA3B9AE8-EFD9-E411-9BA3-0025904B1FB8.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FAD9634A-EFD9-E411-AF00-02163E00EAC0.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FCACD25B-EFD9-E411-B47F-02163E00EB06.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FE353FDD-EED9-E411-9A3A-02163E00E7F8.root',
        '/store/mc/RunIIWinter15wmLHE/TT_13TeV-powheg/LHE/MCRUN2_71_V1_ext1-v1/40000/FEAE2677-EFD9-E411-B1C4-02163E00E966.root',

    ),
    inputCommands = cms.untracked.vstring('keep *', 
        'drop LHEXMLStringProduct_*_*_*'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
 wantSummary = cms.untracked.bool(True)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/GenProduction/python/TOP-RunIIWinter15GS-00001-fragment.py nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

#pythia 8 config
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *
process.generator = cms.EDFilter("Pythia8HadronizerFilter",
                                 maxEventsToPrint = cms.untracked.int32(0),
                                 pythiaPylistVerbosity = cms.untracked.int32(0),
                                 filterEfficiency = cms.untracked.double(1.0),
                                 pythiaHepMCVerbosity = cms.untracked.bool(False),
                                 comEnergy = cms.double(13000.),
                                 PythiaParameters = cms.PSet( pythia8CommonSettingsBlock,
                                                              pythia8CUEP8M1SettingsBlock,
                                                              pythia8PowhegEmissionVetoSettingsBlock,
                                                              processParameters = cms.vstring( 'POWHEG:nFinal = 2',
                                                                                               'TimeShower:mMaxGamma = 1.0',
                                                                                               'TimeShower:renormMultFac   = 1',
                                                                                               'TimeShower:factorMultFac   = 1',
                                                                                               'TimeShower:MEcorrections   = on'											      
                                                                                               ),
                                                              parameterSets = cms.vstring('pythia8CommonSettings',
                                                                                          'pythia8CUEP8M1Settings',
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
process.generation_step = cms.Path(process.pgen)
process.AnalysisSequence = cms.Path(process.genParticles2HepMC*process.particleLevel*process.bfragAnalysis)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.AnalysisSequence,process.genfiltersummary_step,process.endjob_step)

# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path)._seq = process.ProductionFilterSequence * getattr(process,path)._seq 



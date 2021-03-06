from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')

options.register('isMC', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)
options.register('globalTag', 'NOTSET',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Set global tag"
)
options.register('wantSummary', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)
options.register('wantFullRECO', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)
options.register('reportEvery', 10,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "report every N events"
)
options.register('skip', 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "skip first N events"
)

options.setDefault('maxEvents', 500)
options.setDefault('tag', '10215')
options.parseArguments()

globaltag = '102X_dataRun2_v11' if not options.isMC else '102X_upgrade2018_realistic_v15'
if options._beenSet['globalTag']:
    globaltag = options.globalTag

extension = {False : 'data', True : 'mc'}
outputFileNANO = cms.untracked.string('_'.join(['BParkNANO', extension[options.isMC], options.tag])+'.root')
outputFileFEVT = cms.untracked.string('_'.join(['BParkFullEvt', extension[options.isMC], options.tag])+'.root')
if not options.inputFiles:
    options.inputFiles = ['file:/afs/cern.ch/user/d/dryu/BFrag/CMSSW_10_2_15_skim/src/PhysicsTools/BParkingNano/test/BdToKstarJpsi_ToKPiMuMu_probefilter_SoftQCDnonD_TuneCP5_13TeV-pythia8-evtgen_BF7A19E8-ED80-B841-A6EB-B583F36C1125.root']
    # options.inputFiles = ['file:/afs/cern.ch/user/d/dryu/BFrag/CMSSW_10_2_15_skim/src/PhysicsTools/BParkingNano/test/BsToPhiJpsi_ToKKMuMu_probefilter_SoftQCDnonD_TuneCP5_13TeV-pythia8-evtgen_E313F59A-3E16-2342-B628-305F2AEEDCC5.root']
    #options.inputFiles = ['/store/data/Run2018B/ParkingBPH4/MINIAOD/05May2019-v2/230000/6B5A24B1-0E6E-504B-8331-BD899EB60110.root'] if not options.isMC else \
    #                     ['/store/cmst3/group/bpark/BToKmumu_1000Events_MINIAOD.root']

annotation = '%s nevts:%d' % (outputFileNANO, options.maxEvents)

from Configuration.StandardSequences.Eras import eras
process = cms.Process('BParkNANO',eras.Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('PhysicsTools.BParkingNano.nanoBPark_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents=cms.untracked.uint32(options.skip),
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
)

process.nanoMetadata.strings.tag = annotation
# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string(annotation),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileFEVT,
    outputCommands = (cms.untracked.vstring('keep *',
                                            'drop *_*_SelectedTransient*_*',
                     )),
    splitLevel = cms.untracked.int32(0)
)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileNANO,
    outputCommands = cms.untracked.vstring(
      'drop *',
      "keep nanoaodFlatTable_*Table_*_*",     # event data
      "keep nanoaodUniqueString_nanoMetadata_*_*",   # basic metadata
    )

)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

from PhysicsTools.BParkingNano.nanoBPark_cff import *
process = nanoAOD_customizeMuonTriggerBPark(process)
process = nanoAOD_customizeElectronFilteredBPark(process)
process = nanoAOD_customizeTrackFilteredBPark(process)
process = nanoAOD_customizeBToKLL(process)
#process = nanoAOD_customizeBToKstarEE(process)
process = nanoAOD_customizeBToKstarMuMu(process)
#process = nanoAOD_customizeBToPhiEE(process)
process = nanoAOD_customizeBToPhiMuMu(process)
process = nanoAOD_customizeTriggerBitsBPark(process)

# No skim on MC
if options.isMC:
    CountBToKmumu.minNumber     = 0
    CountBToKee.minNumber       = 0
    CountBToKstarMuMu.minNumber = 0
    CountBToKstarEE.minNumber   = 0
    CountBToPhiMuMu.minNumber   = 0
    CountBToPhiEE.minNumber     = 0

# Path and EndPath definitions
process.nanoAOD_KMuMu_step = cms.Path(process.nanoSequence + process.nanoBKMuMuSequence + CountBToKmumu )
#process.nanoAOD_Kee_step   = cms.Path(process.nanoSequence + process.nanoBKeeSequence   + CountBToKee   )
process.nanoAOD_KstarMuMu_step = cms.Path(process.nanoSequence + process.KstarToKPiSequence + process.nanoBKstarMuMuSequence + CountBToKstarMuMu )
#process.nanoAOD_KstarEE_step  = cms.Path(process.nanoSequence+ process.KstarToKPiSequence + process.nanoBKstarEESequence + CountBToKstarEE  )
process.nanoAOD_PhiMuMu_step = cms.Path(process.nanoSequence + process.PhiToKKSequence + process.nanoBPhiMuMuSequence + CountBToPhiMuMu )
#process.nanoAOD_PhiEE_step  = cms.Path(process.nanoSequence+ process.PhiToKKSequence + process.nanoBPhiEESequence + CountBToPhiEE  )

# customisation of the process.
if options.isMC:
    from PhysicsTools.BParkingNano.nanoBPark_cff import nanoAOD_customizeMC
    nanoAOD_customizeMC(process)
    process.countTrgMuons.minNumber = 0

process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(
                                process.nanoAOD_KMuMu_step,
                                #process.nanoAOD_Kee_step, 
                                process.nanoAOD_KstarMuMu_step,
                                #process.nanoAOD_KstarEE_step,
                                process.nanoAOD_PhiMuMu_step,
                                #process.nanoAOD_PhiEE_step,
                                process.endjob_step, 
                                process.NANOAODoutput_step
                               )
if options.wantFullRECO:
    process.schedule = cms.Schedule(
                                    process.nanoAOD_KMuMu_step,
                                    #process.nanoAOD_Kee_step, 
                                    process.nanoAOD_KstarMuMu_step,
                                    #process.nanoAOD_KstarEE_step,
                                    process.nanoAOD_PhiMuMu_step,
                                    #process.nanoAOD_PhiEE_step,
                                    process.endjob_step, 
                                    process.FEVTDEBUGHLToutput_step, 
                                    process.NANOAODoutput_step
                                    )
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring(
                                   'nanoAOD_KMuMu_step', 
                                   #'nanoAOD_Kee_step',
                                   'nanoAOD_KstarMuMu_step',
                                   #'nanoAOD_KstarEE_step',
                                   'nanoAOD_PhiMuMu_step',
                                   #'nanoAOD_PhiEE_step',
                                   )
)


### from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3287/1/1/1/1/1.html
process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab=cms.untracked.bool(True)    

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
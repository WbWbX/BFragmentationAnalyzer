#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

//
JetFragInfo_t analyzeJet(const reco::GenJet &genJet,float tagScale)
{
  //loop over the constituents to analyze the jet leading pT tag and the neutrinos
  std::vector< const reco::Candidate * > jconst=genJet.getJetConstituentsQuick();
  const reco::Candidate *leadTagConst=0;
  bool hasSemiLepDecay(false),hasTauNeutrino(false);
  int nbtags(0),nctags(0),ntautags(0);
  for(size_t ijc=0; ijc <jconst.size(); ijc++) 
    {
      const reco::Candidate *par=jconst[ijc];
      int absid=abs(par->pdgId());

      //account for neutrinos or charged leptons in the final state
      //as an hint of semi-leptonic decays
      if(par->status()==1 && (IS_NEUTRINO_PDGID(absid) || IS_CHLEPTON_PDGID(absid))) 
	{
	  if(absid==16) hasTauNeutrino=true;
	  hasSemiLepDecay=true;
	}
      if(par->status()!=2) continue;
      
      //count number of tags
      if(absid==15)               ntautags++;
      if(IS_BHADRON_PDGID(absid)) nbtags++;
      if(IS_CHADRON_PDGID(absid)) nctags++;

      //save leading pT tag
      if(leadTagConst && leadTagConst->pt()>par->pt()) continue;
      leadTagConst=par;
    }
      
  //fill the jet info
  JetFragInfo_t jinfo;
  reco::Candidate::LorentzVector totalP4(genJet.p4());
  jinfo.xb              = leadTagConst ? (leadTagConst->pt()*tagScale)/totalP4.pt() : -1;
  jinfo.leadTagId       = leadTagConst ? leadTagConst->pdgId() : 0;
  jinfo.hasSemiLepDecay = hasSemiLepDecay;
  jinfo.hasTauSemiLepDecay = hasTauNeutrino;
  jinfo.nbtags          = nbtags;
  jinfo.nctags          = nctags;
  jinfo.ntautags        = ntautags;

  return jinfo;
}

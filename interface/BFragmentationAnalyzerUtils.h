#ifndef _BFragmentationAnalyzerUtils_h_
#define _BFragmentationAnalyzerUtils_h_

#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#define IS_BHADRON_PDGID(id) ( ((abs(id)/100)%10 == 5) || (abs(id) >= 5000 && abs(id) <= 5999) )
#define IS_CHADRON_PDGID(id) ( ((abs(id)/100)%10 == 4) || (abs(id) >= 4000 && abs(id) <= 4999) )
#define IS_NEUTRINO_PDGID(id) ( (abs(id) == 12) || (abs(id) == 14) || (abs(id) == 16) )
#define IS_CHLEPTON_PDGID(id) ( (abs(id) == 11) || (abs(id) == 13) || (abs(id) == 15) )

#define TAG_SCALE 1e+20

struct JetFragInfo_t
{
  float xb_lead, xb_subLead;
  int leadTagId, subLeadTagId;
  float xb_lead_B, xb_subLead_B;
  int leadTagId_B, subLeadTagId_B;
  bool hasSemiLepDecay,hasTauSemiLepDecay;
  int nbtags,nctags,ntautags;
};

JetFragInfo_t analyzeJet(const reco::GenJet &genJet,float tagScale=TAG_SCALE);

#endif

#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

//
JetFragInfo_t analyzeJet(const reco::GenJet& genJet, float tagScale) {
  //loop over the constituents to analyze the jet leading pT tag and the neutrinos
  std::vector<const reco::GenParticle*> jconst = genJet.getGenConstituents();
  std::vector<const reco::Candidate*> tagConst;
  std::vector<const reco::Candidate*> tagConst_B;
  std::vector<const reco::Candidate*> tag_semiLep;
  std::vector<const reco::Candidate*> tag_tauSemiLep;
  int nbtags(0), nctags(0);

  for (size_t ijc = 0; ijc < jconst.size(); ijc++) {
    const reco::GenParticle* par = jconst[ijc];

    int absid = abs(par->pdgId());

    // Look for neutrinos or charged leptons (status-1 e/mu or status-2 taus) in the final state with a B hadron as a parent
    // to tag semileptonic B decays
    if ((par->status() == 2 || par->status() == 1) && (IS_NEUTRINO_PDGID(absid) || IS_CHLEPTON_PDGID(absid))) {
      const reco::Candidate* leptonMother = par->mother();
      if (!leptonMother) {
        continue;
      }
      int motherId = abs(leptonMother->pdgId());
      if (leptonMother->status() != 2 || !IS_BHADRON_PDGID(motherId)) {
        continue;
      }
      // the mother of this lepton is a status-2 B hadron -> store the hadron
      tag_semiLep.push_back(leptonMother);
      if (absid == 16 || absid == 15) {
        tag_tauSemiLep.push_back(leptonMother);
      }
    }

    if (par->status() != 2) {
      continue;
    }

    //count number of tags
    if (IS_BHADRON_PDGID(absid)) {
      nbtags++;
    }
    if (IS_CHADRON_PDGID(absid)) {
      nctags++;
    }

    // to find leading tag particle, regardless of flavour
    tagConst.push_back(par);
    // to find leading B hadron tag particle
    if (IS_BHADRON_PDGID(absid)) {
      tagConst_B.push_back(par);
    }
  }

  auto sortByDecrPt = [](const reco::Candidate* a, const reco::Candidate* b) { return a->pt() > b->pt(); };
  std::sort(tagConst.begin(), tagConst.end(), sortByDecrPt);
  std::sort(tagConst_B.begin(), tagConst_B.end(), sortByDecrPt);

  // fill the jet info
  JetFragInfo_t jinfo;
  reco::Candidate::LorentzVector totalP4(genJet.p4());

  // filling only if the leading ghost hadron in the jet, regardless of flavour (this is not used anymore for fragmentation weights)
  jinfo.xb_lead = (tagConst.size() > 0) ? (tagConst[0]->pt() * tagScale) / totalP4.pt() : -1;
  jinfo.leadTagId = (tagConst.size() > 0) ? tagConst[0]->pdgId() : 0;
  jinfo.xb_subLead = (tagConst.size() > 1) ? (tagConst[1]->pt() * tagScale) / totalP4.pt() : -1;
  jinfo.subLeadTagId = (tagConst.size() > 1) ? tagConst[1]->pdgId() : 0;

  // filled with leading B ghost hadron in the jet (even if there is another hadron with higher pt)
  jinfo.xb_lead_B = (tagConst_B.size() > 0) ? (tagConst_B[0]->pt() * tagScale) / totalP4.pt() : -1;
  jinfo.leadTagId_B = (tagConst_B.size() > 0) ? tagConst_B[0]->pdgId() : 0;
  jinfo.xb_subLead_B = (tagConst_B.size() > 1) ? (tagConst_B[1]->pt() * tagScale) / totalP4.pt() : -1;
  jinfo.subLeadTagId_B = (tagConst_B.size() > 1) ? tagConst_B[1]->pdgId() : 0;

  // tag the jet as having a semi-lep B decay if the leading B hadron is in the list of semileptonically decaying B hadrons
  jinfo.hasSemiLepDecay = false;
  jinfo.hasTauSemiLepDecay = false;
  if (tagConst_B.size() > 0) {
    const auto& b = tagConst_B.at(0);
    if (std::find(tag_semiLep.begin(), tag_semiLep.end(), b) != tag_semiLep.end()) {
      jinfo.hasSemiLepDecay = true;
    }
    if (std::find(tag_tauSemiLep.begin(), tag_tauSemiLep.end(), b) != tag_tauSemiLep.end()) {
      jinfo.hasTauSemiLepDecay = true;
    }
  }

  jinfo.nbtags = nbtags;
  jinfo.nctags = nctags;

  return jinfo;
}

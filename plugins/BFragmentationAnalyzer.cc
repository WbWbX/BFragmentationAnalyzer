#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TH1F.h"
#include "TH2F.h"
#include <iostream>
#include <vector>
#include <map>
#include <algorithm>

#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

using namespace std;

class BFragmentationAnalyzer : public edm::EDAnalyzer {
public:
  explicit BFragmentationAnalyzer(const edm::ParameterSet&);
  ~BFragmentationAnalyzer();
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  virtual void endRun(const edm::Run&, const edm::EventSetup&);

private:
  virtual void beginJob() override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  virtual void endJob() override;

  std::vector<int> hadronList_;
  std::map<std::string, TH1*> histos_;
  edm::Service<TFileService> fs;
  edm::EDGetTokenT<std::vector<reco::GenJet> > genJetsToken_;
};

//
BFragmentationAnalyzer::BFragmentationAnalyzer(const edm::ParameterSet& iConfig)
    : hadronList_(iConfig.getParameter<std::vector<int> >("hadronList")),
      genJetsToken_(consumes<std::vector<reco::GenJet> >(edm::InputTag("particleLevel:jets"))) {
  float xb_binning[124] = {0.0,  0.02,  0.04, 0.06,  0.08, 0.1,   0.12, 0.14,  0.16, 0.18,  0.2,  0.22,  0.24, 0.26,
                           0.28, 0.3,   0.32, 0.34,  0.36, 0.38,  0.4,  0.41,  0.42, 0.43,  0.44, 0.45,  0.46, 0.47,
                           0.48, 0.49,  0.5,  0.51,  0.52, 0.53,  0.54, 0.55,  0.56, 0.57,  0.58, 0.59,  0.6,  0.605,
                           0.61, 0.615, 0.62, 0.625, 0.63, 0.635, 0.64, 0.645, 0.65, 0.655, 0.66, 0.665, 0.67, 0.675,
                           0.68, 0.685, 0.69, 0.695, 0.7,  0.705, 0.71, 0.715, 0.72, 0.725, 0.73, 0.735, 0.74, 0.745,
                           0.75, 0.755, 0.76, 0.765, 0.77, 0.775, 0.78, 0.785, 0.79, 0.795, 0.8,  0.805, 0.81, 0.815,
                           0.82, 0.825, 0.83, 0.835, 0.84, 0.845, 0.85, 0.855, 0.86, 0.865, 0.87, 0.875, 0.88, 0.885,
                           0.89, 0.895, 0.9,  0.905, 0.91, 0.915, 0.92, 0.925, 0.93, 0.935, 0.94, 0.945, 0.95, 0.955,
                           0.96, 0.965, 0.97, 0.975, 0.98, 0.985, 0.99, 0.995, 1.0,  1.05,  1.1,  1.5};
  float pt_binning[12] = {20., 40., 60., 100., 150., 200., 350., 500., 5000.};
  //prepare monitoring histograms

  size_t nhadrons = hadronList_.size();
  // only for B->e/mu+X
  histos_["semilepbr"] = fs->make<TH1F>("semilepbr", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for B->l+X including taus
  histos_["semilepbrinc"] = fs->make<TH1F>("semilepbrinc", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for normalizing the BRs
  histos_["semilepbr_norm"] = fs->make<TH1F>("semilepbr_norm", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for all B hadrons
  histos_["semilepbr"]->GetXaxis()->SetBinLabel(1, "all");
  histos_["semilepbrinc"]->GetXaxis()->SetBinLabel(1, "all");
  histos_["semilepbr_norm"]->GetXaxis()->SetBinLabel(1, "all");

  for (size_t i = 0; i < nhadrons; i++) {
    // for specific B hadrons
    std::string id = std::to_string(hadronList_.at(i));
    histos_["semilepbr"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
    histos_["semilepbrinc"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
    histos_["semilepbr_norm"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
  }

  for (std::string name : {"inc", "B"}) {
    histos_["xb_lead_" + name] = fs->make<TH1F>(
        ("xb_lead_" + name).c_str(), (name + ";x_{b}=p_{T}(B)/p_{T}(jet); Jets").c_str(), 123, xb_binning);
    histos_["xb_pt_lead_" + name] = fs->make<TH2F>(("xb_pt_lead_" + name).c_str(),
                                                   (name + ";x_{b}=p_{T}(B)/p_{T}(jet);p_{T}(jet);Jets").c_str(),
                                                   123,
                                                   xb_binning,
                                                   8,
                                                   pt_binning);
    histos_["xb_subLead_" + name] = fs->make<TH1F>(
        ("xb_subLead_" + name).c_str(), (name + ";x_{b}=p_{T}(B)/p_{T}(jet); Jets").c_str(), 123, xb_binning);
    histos_["xb_pt_subLead_" + name] = fs->make<TH2F>(("xb_pt_subLead_" + name).c_str(),
                                                      (name + ";x_{b}=p_{T}(B)/p_{T}(jet);p_{T}(jet);Jets").c_str(),
                                                      123,
                                                      xb_binning,
                                                      8,
                                                      pt_binning);
  }
  histos_["nbtags"] = fs->make<TH1F>("nbtags", "#nBTags;Jets", 5, 0, 5);
  histos_["nctags"] = fs->make<TH1F>("nctags", "#nCTags;Jets", 5, 0, 5);
  for (auto it : histos_)
    it.second->Sumw2();
}

//
BFragmentationAnalyzer::~BFragmentationAnalyzer() {}

//
void BFragmentationAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  //
  edm::Handle<std::vector<reco::GenJet> > genJets;
  iEvent.getByToken(genJetsToken_, genJets);
  for (auto genJet : *genJets) {
    //map the gen particles which are clustered in this jet
    JetFragInfo_t jinfo = analyzeJet(genJet);

    histos_["nbtags"]->Fill(jinfo.nbtags);
    histos_["nctags"]->Fill(jinfo.nctags);

    if (jinfo.nbtags == 0)
      continue;

    if (IS_BHADRON_PDGID(abs(jinfo.leadTagId))) {
      histos_["xb_lead_inc"]->Fill(jinfo.xb_lead);
      histos_["xb_pt_lead_inc"]->Fill(jinfo.xb_lead, genJet.pt());
    }
    if (IS_BHADRON_PDGID(abs(jinfo.subLeadTagId))) {
      histos_["xb_subLead_inc"]->Fill(jinfo.xb_subLead);
      histos_["xb_pt_subLead_inc"]->Fill(jinfo.xb_subLead, genJet.pt());
    }
    histos_["xb_lead_B"]->Fill(jinfo.xb_lead_B);
    histos_["xb_pt_lead_B"]->Fill(jinfo.xb_lead_B, genJet.pt());
    histos_["xb_subLead_B"]->Fill(jinfo.xb_subLead_B);
    histos_["xb_pt_subLead_B"]->Fill(jinfo.xb_subLead_B, genJet.pt());

    int absid = abs(jinfo.leadTagId_B);
    //exclusive histograms
    std::vector<int>::iterator hit = std::find(hadronList_.begin(), hadronList_.end(), absid);
    histos_["semilepbr_norm"]->Fill(0);
    if (hit != hadronList_.end()) {
      histos_["semilepbr_norm"]->Fill(1 + hit - hadronList_.begin());
    }
    if (jinfo.hasSemiLepDecay) {
      //inclusive histos
      if (!jinfo.hasTauSemiLepDecay)
        histos_["semilepbr"]->Fill(0);
      histos_["semilepbrinc"]->Fill(0);

      if (hit != hadronList_.end()) {
        if (!jinfo.hasTauSemiLepDecay)
          histos_["semilepbr"]->Fill(1 + hit - hadronList_.begin());
        histos_["semilepbrinc"]->Fill(1 + hit - hadronList_.begin());
      }
    }
  }
}

//
void BFragmentationAnalyzer::beginJob() {}

//
void BFragmentationAnalyzer::endRun(const edm::Run& iRun, const edm::EventSetup& iSetup) {}

//
void BFragmentationAnalyzer::endJob() {}

//
void BFragmentationAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BFragmentationAnalyzer);

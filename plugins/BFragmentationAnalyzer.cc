#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

#include "TH1D.h"
#include "TH2D.h"
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
  const edm::EDGetTokenT<std::vector<reco::GenJet> > genJetsToken_;
  std::map<std::string, edm::EDGetTokenT<edm::ValueMap<float>>> weightTokens_;
  const edm::EDGetTokenT<GenEventInfoProduct> genTag_;
  // debugging: also filling histograms while applying weights derived from a previous round, for validation
  const bool debug_;
  std::vector<std::string> debugWeights_ { "fragCP5BL", "fragCP5BLdown", "fragCP5BLup", "fragCP5Peterson", "fragCP5Petersondown", "fragCP5Petersonup", "fragCUETP8M2T4BL", "fragCUETP8M2T4BLdefault", "fragCUETP8M2T4BLLHC", "fragCUETP8M2T4BLLHCdown", "fragCUETP8M2T4BLLHCup" };
};

//
BFragmentationAnalyzer::BFragmentationAnalyzer(const edm::ParameterSet& iConfig)
    : hadronList_(iConfig.getParameter<std::vector<int> >("hadronList")),
      genJetsToken_(consumes<std::vector<reco::GenJet> >(edm::InputTag("particleLevel:jets"))),
      genTag_(consumes<GenEventInfoProduct>(edm::InputTag("generator"))),
      debug_(iConfig.getUntrackedParameter<bool>("debug", false)) {
  // hardcoded xb and pt binnings...
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
  
  // prepare monitoring histograms

  // B semileptonic branching ratios: only for debugging,
  // checking that the BRs measured in the simulation match the pythia input values
  size_t nhadrons = hadronList_.size();
  // only for B->e/mu+X
  histos_["semilepbr"] = fs->make<TH1D>("semilepbr", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for B->l+X including taus
  histos_["semilepbrinc"] = fs->make<TH1D>("semilepbrinc", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for easy normalizing the BRs to the total number of entries
  histos_["semilepbr_norm"] = fs->make<TH1D>("semilepbr_norm", ";B-hadron;BR", nhadrons + 1, 0, nhadrons + 1);
  // for all B hadrons
  histos_["semilepbr"]->GetXaxis()->SetBinLabel(1, "all");
  histos_["semilepbrinc"]->GetXaxis()->SetBinLabel(1, "all");
  histos_["semilepbr_norm"]->GetXaxis()->SetBinLabel(1, "all");

  for (size_t i = 0; i < nhadrons; i++) {
    // for specific B hadron PDGids
    std::string id = std::to_string(hadronList_.at(i));
    histos_["semilepbr"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
    histos_["semilepbrinc"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
    histos_["semilepbr_norm"]->GetXaxis()->SetBinLabel(i + 2, id.c_str());
  }

  // "inc" -> take leading matched hadron, fill only if it's a B
  // "B"   -> take leading matched B hadron
  for (std::string name : {"inc", "B"}) {
    // leading hadron
    // xb only
    histos_["xb_lead_" + name] = fs->make<TH1D>(
        ("xb_lead_" + name).c_str(), (name + ";x_{b}=p_{T}(B)/p_{T}(jet); Jets").c_str(), 123, xb_binning);
    // xb vs. pt
    histos_["xb_pt_lead_" + name] = fs->make<TH2D>(("xb_pt_lead_" + name).c_str(),
                                                   (name + ";x_{b}=p_{T}(B)/p_{T}(jet);p_{T}(jet);Jets").c_str(),
                                                   123,
                                                   xb_binning,
                                                   8,
                                                   pt_binning);
    // sub-leading hadron
    // xb only
    histos_["xb_subLead_" + name] = fs->make<TH1D>(
        ("xb_subLead_" + name).c_str(), (name + ";x_{b}=p_{T}(B)/p_{T}(jet); Jets").c_str(), 123, xb_binning);
    // xb vs. pt
    histos_["xb_pt_subLead_" + name] = fs->make<TH2D>(("xb_pt_subLead_" + name).c_str(),
                                                      (name + ";x_{b}=p_{T}(B)/p_{T}(jet);p_{T}(jet);Jets").c_str(),
                                                      123,
                                                      xb_binning,
                                                      8,
                                                      pt_binning);
  }
  histos_["nbtags"] = fs->make<TH1D>("nbtags", "nBTags;Jets", 5, 0, 5);
  histos_["nctags"] = fs->make<TH1D>("nctags", "nCTags;Jets", 5, 0, 5);
  histos_["nJets"] = fs->make<TH1D>("nJets", "nGenJets;Events", 15, 0, 15);
  histos_["norm"] = fs->make<TH1D>("norm", "norm;Events", 1, 0, 1);
  histos_["pt"] = fs->make<TH1D>("pt", "pt;Events", 500, 0, 1000);

  // debugging: apply weights derived from a previous round
  if (debug_) {
      std::size_t nWgt = debugWeights_.size();
      for (std::size_t im = 0; im < nWgt; im++) {
          debugWeights_.push_back(debugWeights_[im] + "VsPt");
      }

      for (const auto& nm: debugWeights_) {
          weightTokens_[nm] = consumes<edm::ValueMap<float>>(edm::InputTag("bfragWgtProducer:" + nm));

          histos_["debug_xb_lead_B_" + nm] = fs->make<TH1D>(
            ("debug_xb_lead_B_" + nm).c_str(), "B;x_{b}=p_{T}(B)/p_{T}(jet); Jets", 123, xb_binning);
          histos_["debug_xb_pt_lead_B_" + nm] = fs->make<TH2D>(("debug_xb_pt_lead_B_" + nm).c_str(),
                                                       "B;x_{b}=p_{T}(B)/p_{T}(jet);p_{T}(jet);Jets",
                                                       123,
                                                       xb_binning,
                                                       8,
                                                       pt_binning);
          histos_["debug_nJets_" + nm] = fs->make<TH1D>(("debug_nJets_" + nm).c_str(), "#nGenJets;Events", 15, 0, 15);
          histos_["debug_norm_" + nm] = fs->make<TH1D>(("debug_norm_" + nm).c_str(), "#norm;Events", 1, 0, 1);
          histos_["debug_pt_" + nm] = fs->make<TH1D>(("debug_pt_" + nm).c_str(), "pt;Events", 500, 0, 1000);
      }
  }

  for (auto it: histos_) {
    it.second->Sumw2();
  }
}

//
BFragmentationAnalyzer::~BFragmentationAnalyzer() {}

//
void BFragmentationAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  //
  edm::Handle<std::vector<reco::GenJet> > genJets;
  iEvent.getByToken(genJetsToken_, genJets);

  // debugging: for retrieving weights from a previous round
  std::map<std::string, float> debugWeightProducts;
  std::map<std::string, edm::Handle<edm::ValueMap<float>>> weightHandles;
  for (auto& wgt_token : weightTokens_) {
    edm::Handle<edm::ValueMap<float>> handle;
    iEvent.getByToken(wgt_token.second, handle);
    weightHandles.emplace(wgt_token.first, handle);
    debugWeightProducts.emplace(wgt_token.first, 1.);
  }

  edm::Handle<GenEventInfoProduct> genInfo;
  iEvent.getByToken(genTag_, genInfo);
  // double weight = genInfo->weight(); // event weight: not used...
  
  std::size_t nJets = genJets->size();
  histos_["nJets"]->Fill(nJets);
  histos_["norm"]->Fill(0.);

  for (std::size_t iJet=0; iJet < nJets; iJet++) {
    const reco::GenJet genJet = genJets->at(iJet);
    // analyze the "tag" gen particles which are clustered in this jet
    JetFragInfo_t jinfo = analyzeJet(genJet);

    histos_["nbtags"]->Fill(jinfo.nbtags);
    histos_["nctags"]->Fill(jinfo.nctags);

    if (jinfo.nbtags == 0) {
      continue;
    }

    histos_["pt"]->Fill(genJet.pt());

    // fill only if leading tag hadron is a B hadron
    if (IS_BHADRON_PDGID(abs(jinfo.leadTagId))) {
      histos_["xb_lead_inc"]->Fill(jinfo.xb_lead);
      static_cast<TH2*>(histos_["xb_pt_lead_inc"])->Fill(jinfo.xb_lead, genJet.pt());
    }
    // fill only if sub-leading tag hadron is a B hadron
    if (IS_BHADRON_PDGID(abs(jinfo.subLeadTagId))) {
      histos_["xb_subLead_inc"]->Fill(jinfo.xb_subLead);
      static_cast<TH2*>(histos_["xb_pt_subLead_inc"])->Fill(jinfo.xb_subLead, genJet.pt());
    }
    // fill with leading tag B hadron (might not exist)
    histos_["xb_lead_B"]->Fill(jinfo.xb_lead_B);
    static_cast<TH2*>(histos_["xb_pt_lead_B"])->Fill(jinfo.xb_lead_B, genJet.pt());
    // fill with subleading tag B hadron (might not exist)
    histos_["xb_subLead_B"]->Fill(jinfo.xb_subLead_B);
    static_cast<TH2*>(histos_["xb_pt_subLead_B"])->Fill(jinfo.xb_subLead_B, genJet.pt());

    int absid = abs(jinfo.leadTagId_B);
    //exclusive histograms
    std::vector<int>::iterator hit = std::find(hadronList_.begin(), hadronList_.end(), absid);
    histos_["semilepbr_norm"]->Fill(0);
    if (hit != hadronList_.end()) {
      histos_["semilepbr_norm"]->Fill(1 + hit - hadronList_.begin());
    }
    if (jinfo.hasSemiLepDecay) {
      //inclusive histos
      if (!jinfo.hasTauSemiLepDecay) {
        histos_["semilepbr"]->Fill(0);
      }
      histos_["semilepbrinc"]->Fill(0);

      if (hit != hadronList_.end()) {
        if (!jinfo.hasTauSemiLepDecay) {
          histos_["semilepbr"]->Fill(1 + hit - hadronList_.begin());
        }
        histos_["semilepbrinc"]->Fill(1 + hit - hadronList_.begin());
      }
    }

    if (debug_) {
        // jet histograms are filled per jet: for each jet, use the weight computing using this jet
        // note: this is different from an analysis where the weights for all jets are multiplied as an event weight
        edm::Ref<std::vector<reco::GenJet>> genJetRef(genJets, iJet);
        for (auto& wgt_handle: weightHandles) {
            double fragWeight = (*(wgt_handle.second))[genJetRef];
            histos_["debug_pt_" + wgt_handle.first]->Fill(genJet.pt(), fragWeight);
            histos_["debug_xb_lead_B_" + wgt_handle.first]->Fill(jinfo.xb_lead_B, fragWeight);
            static_cast<TH2*>(histos_["debug_xb_pt_lead_B_" + wgt_handle.first])->Fill(jinfo.xb_lead_B, genJet.pt(), fragWeight);
            debugWeightProducts[wgt_handle.first] *= fragWeight;
        }
    }
  }

  if (debug_) {
      // here we use the product of the weights for all jets (histograms filled per event)
      for (auto& nm_wgtProd: debugWeightProducts) {
          histos_["debug_nJets_" + nm_wgtProd.first]->Fill(nJets, nm_wgtProd.second);
          histos_["debug_norm_" + nm_wgtProd.first]->Fill(0., nm_wgtProd.second);
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

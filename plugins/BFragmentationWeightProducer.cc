#include <memory>
#include <string>
#include <map>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/FileInPath.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

#include "TFile.h"
#include "TGraph.h"
#include "TH2.h"

using namespace std;

class BFragmentationWeightProducer : public edm::stream::EDProducer<> {
public:
  explicit BFragmentationWeightProducer(const edm::ParameterSet&);
  ~BFragmentationWeightProducer();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  virtual void beginStream(edm::StreamID) override;
  virtual void produce(edm::Event&, const edm::EventSetup&) override;
  virtual void endStream() override;

  edm::EDGetTokenT<std::vector<reco::GenJet>> genJetsToken_;
  const std::vector<std::string> br_weights_;
  const std::vector<std::string> frag_weights_;
  const std::vector<std::string> frag_weights_vs_pt_;
  std::map<std::string, TGraph*> brWgtGr_;     // BR weights are stored as graphs
  std::map<std::string, TH2*> fragWgtPtHist_;  // frag weights vs. pt are stored as histograms
  std::map<std::string, TGraph*> fragWgtGr_;   // pt-averaged frag weights are stored as graphs
};

//
BFragmentationWeightProducer::BFragmentationWeightProducer(const edm::ParameterSet& iConfig)
    : genJetsToken_(consumes<std::vector<reco::GenJet>>(iConfig.getParameter<edm::InputTag>("src"))),
      br_weights_(iConfig.getParameter<std::vector<std::string>>("br_weights")),
      frag_weights_(iConfig.getParameter<std::vector<std::string>>("frag_weights")),
      frag_weights_vs_pt_(iConfig.getParameter<std::vector<std::string>>("frag_weights_vs_pt")) {
  //readout weights from file and declare them for the producer

  edm::FileInPath fp = iConfig.getParameter<edm::FileInPath>("br_weight_file");
  TFile* fIn = TFile::Open(fp.fullPath().c_str());
  for (const auto& wgt : br_weights_) {
    produces<edm::ValueMap<float>>(wgt);
    TGraph* gr = static_cast<TGraph*>(fIn->Get(wgt.c_str()));
    if (!gr)
      throw cms::Exception("ObjectNotFound")
          << "Could not load object " << wgt << " from " << fp.fullPath() << std::endl;
    brWgtGr_[wgt] = gr;
  }
  fIn->Close();

  fp = iConfig.getParameter<edm::FileInPath>("frag_weight_file");
  fIn = TFile::Open(fp.fullPath().c_str());
  for (const auto& wgt : frag_weights_) {
    produces<edm::ValueMap<float>>(wgt);
    std::string grName = wgt + "_smooth";
    TGraph* gr = static_cast<TGraph*>(fIn->Get(grName.c_str()));
    if (!gr)
      throw cms::Exception("ObjectNotFound")
          << "Could not load object " << grName << " from " << fp.fullPath() << std::endl;
    fragWgtGr_[wgt] = gr;
  }
  fIn->Close();

  fp = iConfig.getParameter<edm::FileInPath>("frag_weight_vs_pt_file");
  fIn = TFile::Open(fp.fullPath().c_str());
  for (const auto& wgt : frag_weights_vs_pt_) {
    produces<edm::ValueMap<float>>(wgt + "VsPt");
    std::string histName = wgt + "_smooth";
    TH2* hist = static_cast<TH2*>(fIn->Get(histName.c_str()));
    if (!hist)
      throw cms::Exception("ObjectNotFound")
          << "Could not load object " << histName << " from " << fp.fullPath() << std::endl;
    fragWgtPtHist_[wgt] = hist;
  }
  fIn->Close();
}

//
BFragmentationWeightProducer::~BFragmentationWeightProducer() {}

//
void BFragmentationWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  edm::Handle<std::vector<reco::GenJet>> genJets;
  iEvent.getByToken(genJetsToken_, genJets);
  std::map<std::string, std::vector<float>> jetWeights;
  for (const auto& wgt : br_weights_)
    jetWeights[wgt] = std::vector<float>();
  for (const auto& wgt : frag_weights_)
    jetWeights[wgt] = std::vector<float>();
  for (const auto& wgt : frag_weights_vs_pt_)
    jetWeights[wgt + "VsPt"] = std::vector<float>();

  for (auto genJet : *genJets) {
    //map the gen particles which are clustered in this jet
    JetFragInfo_t jinfo = analyzeJet(genJet);

    //evaluate the weight to an alternative fragmentation model (if a tag id is available)
    for (const auto& wgt : frag_weights_) {
      if (jinfo.leadTagId_B != 0 && jinfo.xb_lead_B < 1)  // always store 1 above xb=1
        jetWeights[wgt].push_back(fragWgtGr_[wgt]->Eval(jinfo.xb_lead_B));
      else
        jetWeights[wgt].push_back(1.);
    }

    for (const auto& wgt : frag_weights_vs_pt_) {
      if (jinfo.leadTagId_B != 0 && jinfo.xb_lead_B < 1 && genJet.pt() >= 20) {
        TH2* hist = fragWgtPtHist_[wgt];
        size_t xb_bin = hist->GetXaxis()->FindBin(jinfo.xb_lead_B);
        size_t pt_bin = hist->GetYaxis()->FindBin(genJet.pt());
        float weight = hist->GetBinContent(xb_bin, pt_bin);
        jetWeights[wgt + "VsPt"].push_back(weight);
      } else {
        jetWeights[wgt + "VsPt"].push_back(1.);
      }
    }

    for (const auto& wgt : br_weights_) {
      float weight(1.0);
      int absBid(abs(jinfo.leadTagId_B));
      if (absBid == 511 || absBid == 521 || absBid == 531 || absBid == 5122) {
        int bid(jinfo.hasSemiLepDecay ? absBid : -absBid);
        weight = brWgtGr_[wgt]->Eval(bid);
      }
      jetWeights[wgt].push_back(weight);
    }

    /*
       if(IS_BHADRON_PDGID(absBid))
	 cout << genJet.pt()       << " GeV jet matched with " << absBid 
	      << " upFrag: "       << wgtGr_["upFrag"]->Eval(jinfo.xb)
	      << " centralFrag: "  << wgtGr_["centralFrag"]->Eval(jinfo.xb)
	      << " downFrag: "     << wgtGr_["downFrag"]->Eval(jinfo.xb)
	      << " PetersonFrag: " << wgtGr_["PetersonFrag"]->Eval(jinfo.xb)
	      << " semilep+: "     << semilepbrUp 
	      << " semilep-: "     << semilepbrDown << endl;
       */
  }

  //put in event
  for (auto it : jetWeights) {
    auto valMap = std::make_unique<ValueMap<float>>();
    edm::ValueMap<float>::Filler filler(*valMap);
    filler.insert(genJets, it.second.begin(), it.second.end());
    filler.fill();
    iEvent.put(std::move(valMap), it.first);
  }
}

//
void BFragmentationWeightProducer::beginStream(edm::StreamID) {}

//
void BFragmentationWeightProducer::endStream() {}

//
void BFragmentationWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BFragmentationWeightProducer);

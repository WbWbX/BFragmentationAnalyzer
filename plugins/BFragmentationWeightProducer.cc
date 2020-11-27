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
#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

#include "TFile.h"
#include "TGraph.h"

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

  edm::EDGetTokenT<std::vector<reco::GenJet> > genJetsToken_;
  const std::vector<std::string> weights_;
  std::map<std::string, TGraph *> wgtGr_;
};

//
BFragmentationWeightProducer::BFragmentationWeightProducer(const edm::ParameterSet& iConfig):
  genJetsToken_(consumes<std::vector<reco::GenJet> >(iConfig.getParameter<edm::InputTag>("src"))),
  weights_(iConfig.getParameter<std::vector<std::string>>("weights"))
{
  //readout weights from file and declare them for the producer
  edm::FileInPath fp = iConfig.getParameter<edm::FileInPath>("cfg");
  TFile *fIn = TFile::Open(fp.fullPath().c_str());
  for (const auto& wgt: weights_) {
      produces<edm::ValueMap<float> >(wgt);
      std::string grName = (wgt.find("frag") != std::string::npos) ? (wgt + "_smooth") : wgt; // use the smoothed fragmentation graphs
      TGraph *gr = static_cast<TGraph*>(fIn->Get(grName.c_str()));  
      if (!gr) continue;
      wgtGr_[wgt] = gr;
  }

  fIn->Close();
}

//
BFragmentationWeightProducer::~BFragmentationWeightProducer()
{
}

//
void BFragmentationWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   edm::Handle<std::vector<reco::GenJet> > genJets;
   iEvent.getByToken(genJetsToken_,genJets);
   std::map< std::string, std::vector<float> > jetWeights;
   for (const auto& wgt: weights_)
       jetWeights[wgt] = std::vector<float>();

   for(auto genJet: *genJets) {
       //map the gen particles which are clustered in this jet
       JetFragInfo_t jinfo=analyzeJet(genJet);
       
       //evaluate the weight to an alternative fragmentation model (if a tag id is available)
       for (const auto& wgt: weights_) {
           if (wgt.find("frag") == std::string::npos)
               continue;
           if (jinfo.leadTagId != 0)
               jetWeights[wgt].push_back(wgtGr_[wgt]->Eval(jinfo.xb));
           else
               jetWeights[wgt].push_back(1.);
       }

       float semilepbrUp(1.0), semilepbrDown(1.0);
       int absBid(abs(jinfo.leadTagId));
       if (absBid == 511 || absBid == 521 || absBid == 531 || absBid == 5122) {
           int bid(jinfo.hasSemiLepDecay ? absBid : -absBid);
           semilepbrUp = wgtGr_["semilepbrup"]->Eval(bid);
           semilepbrDown = wgtGr_["semilepbrdown"]->Eval(bid);
	   }
       jetWeights["semilepbrup"].push_back(semilepbrUp);
       jetWeights["semilepbrdown"].push_back(semilepbrDown);

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
   for(auto it: jetWeights) {
       auto valMap = std::make_unique<ValueMap<float> >();
       edm::ValueMap<float>::Filler filler(*valMap);
       filler.insert(genJets, it.second.begin(), it.second.end());
       filler.fill();
       iEvent.put(std::move(valMap), it.first);
   } 
}

//
void BFragmentationWeightProducer::beginStream(edm::StreamID)
{
}

//
void BFragmentationWeightProducer::endStream() {
}

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

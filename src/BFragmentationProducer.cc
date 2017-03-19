#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "Utilities/General/interface/FileInPath.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "TopQuarkAnalysis/BFragmentationAnalyzer/interface/BFragmentationAnalyzerUtils.h"

#include "TFile.h"
#include "TGraph.h"

using namespace std;


class BFragmentationProducer : public edm::stream::EDProducer<> {
   public:
      explicit BFragmentationProducer(const edm::ParameterSet&);
      ~BFragmentationProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginStream(edm::StreamID) override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endStream() override;

  edm::EDGetTokenT<std::vector<reco::GenJet> > genJetsToken_;
};

//
BFragmentationProducer::BFragmentationProducer(const edm::ParameterSet& iConfig):
  genJetsToken_(consumes<std::vector<reco::GenJet> >(edm::InputTag("pseudoTop:jets")))
{
  std::string weights[]={"fragUp","fragDown","semilepUp","semilepDown"};
  for(size_t i=0; i<sizeof(weights)/sizeof(std::string); i++) produces<edm::ValueMap<float> >(weights[i]);

  //readout weights from file
  edm::FileInPath fp = iConfig.getParameter<edm::FileInPath>("cfg");
  TFile *fIn=TFile::Open(fp.fullPath().c_str());
  cout << fIn << endl;
}

//
BFragmentationProducer::~BFragmentationProducer()
{
}

//
void BFragmentationProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   edm::Handle<std::vector<reco::GenJet> > genJets;
   iEvent.getByToken(genJetsToken_,genJets);
   std::map< std::string, std::vector<float> > jetWeights;
   jetWeights["fragUp"]=std::vector<float>();
   jetWeights["fragDown"]=std::vector<float>();
   jetWeights["semilepUp"]=std::vector<float>();
   jetWeights["semilepDown"]=std::vector<float>();
   for(auto genJet : *genJets)
     {
       //map the gen particles which are clustered in this jet
       JetFragInfo_t jinfo=analyzeJet(genJet);
       jetWeights["fragUp"].push_back(jinfo.xb);
       jetWeights["fragDown"].push_back(jinfo.xb);
       jetWeights["semilepUp"].push_back(jinfo.xb);
       jetWeights["semilepDown"].push_back(jinfo.xb);
     }

   //put in event
   for(auto it : jetWeights)
     {
       auto_ptr<ValueMap<float> > valMap(new ValueMap<float>());
       typename edm::ValueMap<float>::Filler filler(*valMap);
       filler.insert(genJets, it.second.begin(), it.second.end());
       filler.fill();
       iEvent.put(valMap, it.first);
     }
}

//
void BFragmentationProducer::beginStream(edm::StreamID)
{
}

//
void BFragmentationProducer::endStream() {
}

//
void BFragmentationProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BFragmentationProducer);

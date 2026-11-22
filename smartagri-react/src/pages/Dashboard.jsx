import { useState } from 'react';
import Header from '../components/Header.jsx';
import Marquee from '../components/Marquee.jsx';
import LanguageSwitcher from '../components/LanguageSwitcher.jsx';
import Footer from '../components/Footer.jsx';
import AskMyFarmSection from '../components/sections/AskMyFarmSection.jsx';
import DiseaseDetectionSection from '../components/sections/DiseaseDetectionSection.jsx';
import MarketPriceSection from '../components/sections/MarketPriceSection.jsx';
import CropRecommendationSection from '../components/sections/CropRecommendationSection.jsx';
import SmartIrrigationSection from '../components/sections/SmartIrrigationSection.jsx';
import PlannerAgentSection from '../components/sections/PlannerAgentSection.jsx';
import DecisionIntelligenceSection from '../components/sections/DecisionIntelligenceSection.jsx';
import AiChatAssistant from '../components/AiChatAssistant.jsx';
import { useLanguage } from '../context/LanguageContext.jsx';
import { api } from '../api.js';

export default function Dashboard({ userName, onLogout }) {
  const { t } = useLanguage();

  // Aggregated state that the Planner Agent section reads from
  const [moduleState, setModuleState] = useState({
    recommendedCrop: '',
    city: '',
    predictedDisease: '',
    priceCrop: '',
    predictedPrice: '',
    irrigationAdvice: ''
  });

  // Comprehensive dashboard context for the AI Agronomist Chatbot
  const [dashboardContext, setDashboardContext] = useState({
    crop: null,
    price: null,
    disease: null,
    irrigation: null,
    planner: null,
    decisionIntelligence: null
  });

  async function handleReset() {
    if (!window.confirm(t('resetConfirm'))) return;
    try {
      await api.resetSession();
    } finally {
      setModuleState({
        recommendedCrop: '',
        city: '',
        predictedDisease: '',
        priceCrop: '',
        predictedPrice: '',
        irrigationAdvice: ''
      });
      setDashboardContext({
        crop: null,
        price: null,
        disease: null,
        irrigation: null,
        planner: null,
        decisionIntelligence: null
      });
      window.location.reload();
    }
  }

  return (
    <>
      <Header userName={userName} onLogout={onLogout} />
      <Marquee />
      <LanguageSwitcher />

      <div className="main-container">
        <div style={{ textAlign: 'right', marginBottom: '8px' }}>
          <button type="button" className="gov-btn reset-btn" onClick={handleReset}>
            {t('resetSession')}
          </button>
        </div>

        <AskMyFarmSection
          moduleState={moduleState}
          onResult={(res) => {
            setDashboardContext((prev) => ({
              ...prev,
              visualCopilot: res
            }));
          }}
        />

        <CropRecommendationSection
          onResult={(res) => {
            const cropName = typeof res === 'object' ? (res.crop || '') : res;
            const cityName = typeof res === 'object' ? (res.city || '') : '';
            const cropDataObj = typeof res === 'object' ? res.data : null;
            setModuleState((prev) => ({ 
              ...prev, 
              recommendedCrop: cropName, 
              city: cityName,
              cropData: cropDataObj,
              priceData: cropDataObj?.price_data || prev.priceData,
              predictedPrice: cropDataObj?.predicted_price || prev.predictedPrice,
              irrigationData: cropDataObj?.irrigation_data || prev.irrigationData
            }));
            setDashboardContext((prev) => ({
              ...prev,
              crop: typeof res === 'object' ? res : { crop: cropName, city: cityName }
            }));
          }}
        />

        <MarketPriceSection
          recommendedCrop={moduleState.recommendedCrop}
          city={moduleState.city}
          onResult={(res) => {
            const cropName = typeof res === 'object' ? (res.crop || '') : '';
            const priceVal = typeof res === 'object' ? (res.priceText || res.price || '') : res;
            setModuleState((prev) => ({ 
              ...prev, 
              priceCrop: cropName, 
              predictedPrice: priceVal,
              priceData: typeof res === 'object' ? res.data : null
            }));
            setDashboardContext((prev) => ({
              ...prev,
              price: typeof res === 'object' ? res : { crop: cropName, priceText: priceVal }
            }));
          }}
        />

        <DiseaseDetectionSection
          recommendedCrop={moduleState.recommendedCrop}
          onResult={(res) => {
            const disName = typeof res === 'object' ? (res.disease || res.result || '') : res;
            setModuleState((prev) => ({ ...prev, predictedDisease: disName }));
            setDashboardContext((prev) => ({
              ...prev,
              disease: typeof res === 'object' ? res : { disease: disName }
            }));
          }}
        />

        <SmartIrrigationSection
          recommendedCrop={moduleState.recommendedCrop}
          city={moduleState.city}
          onResult={(irriData) => {
            setModuleState((prev) => ({
              ...prev,
              irrigationAdvice: irriData?.advice_en || irriData?.advice || '',
              irrigationData: irriData
            }));
            setDashboardContext((prev) => ({
              ...prev,
              irrigation: irriData
            }));
          }}
        />

        <PlannerAgentSection 
          moduleState={moduleState} 
          onResult={(planData) => {
            setDashboardContext((prev) => ({ ...prev, planner: planData }));
          }}
        />

        <DecisionIntelligenceSection 
          moduleState={moduleState} 
          onResult={(diData) => {
            setDashboardContext((prev) => ({ ...prev, decisionIntelligence: diData }));
          }}
        />
      </div>

      <AiChatAssistant dashboardContext={dashboardContext} />
      <Footer />
    </>
  );
}

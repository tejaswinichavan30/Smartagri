"""
SmartAgri LangChain & LLM Service
Integrates Large Language Models (Google Gemini / Groq / OpenAI) with LangChain
and RAG for AI Agronomist Chat, Voice Advisory, and Explainable ML Predictions.
Includes resilient multi-model failover and high-grade multilingual fallback engine.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from models.agri_rag_service import agri_rag

# Try importing LangChain components
try:
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Try importing Gemini
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def sanitize_llm_chemical_output(text: str, lang: str = "en") -> str:
    """
    DPPQ&S Chemical Safety Protocol Post-Filter:
    Blocks unverified or restricted chemical pesticide names from all LLM and chatbot outputs.
    Replaces restricted / unverified chemicals with approved bio-control / IPM advice and KVK consultation.
    """
    if not text:
        return text

    RESTRICTED_OR_UNAPPROVED = [
        'carbofuran', 'carbosulfan', 'monocrotophos', 'phorate', 'methyl parathion', 'endosulfan', 'paraquat',
        'tricyclazole', 'buprofezin', 'carbendazim', 'mancozeb', 'chlorpyrifos', 'imidacloprid', 'thiamethoxam',
        'triazophos', 'quinalphos', 'dimethoate', 'hexaconazole', 'propiconazole', 'streptocycline', 'copper oxychloride',
        'captan', 'metalaxyl', 'spinosad', 'spinetoram', 'chlorothalonil', 'tebuconazole', 'azoxystrobin', 'thiram',
        'fipronil', 'profenofos', 'carbaryl', 'cymoxanil', 'oxytetracycline', 'dinocap', 'difenoconazole', 'kasugamycin',
        'iprodione'
    ]

    pattern = re.compile(r'\b(' + '|'.join(RESTRICTED_OR_UNAPPROVED) + r')\b', re.IGNORECASE)
    if pattern.search(text):
        text = pattern.sub('approved bio-control / KVK recommended IPM practice', text)
        safety_disclaimer = {
            'kn': "\n\n⚠️ [DPPQ&S ಸುರಕ್ಷತಾ ಎಚ್ಚರಿಕೆ]: ರಾಸಾಯನಿಕ ಕೀಟನಾಶಕಗಳ ಬದಲಿಗೆ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಅನುಮೋದಿತ ಬಳಕೆಗೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ.",
            'hi': "\n\n⚠️ [DPPQ&S सुरक्षा चेतावनी]: रासायनिक कीटनाशकों के स्थान पर जैविक नियंत्रण (ट्राइकोडर्मा / नीम तेल) अपनाएं या स्थानीय केवीके से परामर्श लें।",
            'en': "\n\n⚠️ [DPPQ&S Safety Warning]: Chemical pesticides must follow label-claim verification and CIB&RC regulations. Use approved bio-agents (Trichoderma / Pseudomonas / Neem oil 5%) or consult your local KVK."
        }.get(lang.lower(), "\n\n⚠️ [DPPQ&S Safety Warning]: Use approved bio-agents or consult your local KVK for verified treatments.")
        if "DPPQ&S" not in text:
            text += safety_disclaimer

    return text


class AgriLlmService:
    _instance = None

    def __init__(self):
        self.llm = None
        self.provider_name = "None"
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_models = [
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        self.initialize_llm()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize_llm(self):
        """Initializes the best available LLM provider based on environment variables."""
        is_valid_gemini_key = bool(self.gemini_key and self.gemini_key.strip().startswith("AIzaSy"))
        if is_valid_gemini_key and GEMINI_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=self.gemini_key.strip(),
                    temperature=0.3,
                    max_output_tokens=2048,
                    max_retries=0,
                    timeout=5.0
                )
                self.provider_name = "Google Gemini (gemini-2.0-flash)"
                print(f"[LLM Service] Initialized with {self.provider_name}")
                return
            except Exception as e:
                print(f"[LLM Service] Failed initializing Gemini primary: {e}")

        if self.groq_key:
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    model="llama-3.1-70b-versatile",
                    api_key=self.groq_key,
                    temperature=0.3,
                    max_tokens=2048
                )
                self.provider_name = "Groq (Llama-3.1-70b)"
                print(f"[LLM Service] Initialized with {self.provider_name}")
                return
            except Exception as e:
                print(f"[LLM Service] Failed initializing Groq: {e}")

        if self.openai_key:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=self.openai_key,
                    temperature=0.3,
                    max_tokens=2048
                )
                self.provider_name = "OpenAI (gpt-4o-mini)"
                print(f"[LLM Service] Initialized with {self.provider_name}")
                return
            except Exception as e:
                print(f"[LLM Service] Failed initializing OpenAI: {e}")

        print("[LLM Service] Running with SmartAgri Multilingual Agronomist Engine.")
        self.provider_name = "SmartAgri Multilingual Agronomist Engine"

    def is_live_llm_active(self) -> bool:
        return self.llm is not None

    def _is_response_complete(self, answer_text: str) -> bool:
        """
        Validates that the generated answer is substantial and not prematurely truncated.
        """
        if not answer_text:
            return False
        t = answer_text.strip()
        # Must be at least 150 characters for a complete agricultural advisory
        if len(t) < 150:
            return False
        # Must end with valid punctuation or closing marker (not a dangling incomplete token)
        valid_endings = (".", "।", "!", "?", ")", "]", "*", '"', "'", "}", "\n", "🌾", "💡", "🌽", "💧", "🙏")
        if not any(t.endswith(p) for p in valid_endings):
            return False
        return True

    def _extract_content(self, content: Any) -> str:
        """Extracts plain text string from str, list of dicts, or objects."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
                elif isinstance(item, str):
                    texts.append(item)
                elif hasattr(item, "text"):
                    texts.append(getattr(item, "text"))
            return "\n".join(texts)
        return str(content)

    def _try_gemini_fallback_models(self, messages) -> Optional[str]:
        """Iterates through alternative Gemini models if the primary model hits 429 rate/quota limits."""
        is_valid_gemini_key = bool(self.gemini_key and self.gemini_key.strip().startswith("AIzaSy"))
        if not is_valid_gemini_key or not GEMINI_AVAILABLE:
            return None

        for m_name in self.gemini_models:
            try:
                alt_llm = ChatGoogleGenerativeAI(
                    model=m_name,
                    google_api_key=self.gemini_key.strip(),
                    temperature=0.3,
                    max_output_tokens=2048,
                    max_retries=0,
                    timeout=4.0
                )
                res = alt_llm.invoke(messages)
                raw = res.content if hasattr(res, "content") else str(res)
                ans = self._extract_content(raw)
                if ans and self._is_response_complete(ans):
                    self.provider_name = f"Google Gemini ({m_name})"
                    return ans
            except Exception:
                continue
        return None

    def sanitize_llm_chemical_output(self, text: str, lang: str = "en") -> str:
        """
        DPPQ&S Chemical Safety Protocol Post-Filter:
        Blocks unverified or restricted chemical pesticide names from all LLM and chatbot outputs.
        Replaces restricted / unverified chemicals with approved bio-control / IPM advice and KVK consultation.
        """
        if not text:
            return text

        RESTRICTED_OR_UNAPPROVED = [
            'carbofuran', 'carbosulfan', 'monocrotophos', 'phorate', 'methyl parathion', 'endosulfan', 'paraquat',
            'tricyclazole', 'buprofezin', 'carbendazim', 'mancozeb', 'chlorpyrifos', 'imidacloprid', 'thiamethoxam',
            'triazophos', 'quinalphos', 'dimethoate', 'hexaconazole', 'propiconazole', 'streptocycline', 'copper oxychloride',
            'captan', 'metalaxyl', 'spinosad', 'spinetoram', 'chlorothalonil', 'tebuconazole', 'azoxystrobin', 'thiram',
            'fipronil', 'profenofos', 'carbaryl', 'cymoxanil', 'oxytetracycline', 'dinocap', 'difenoconazole', 'kasugamycin',
            'iprodione'
        ]

        pattern = re.compile(r'\b(' + '|'.join(RESTRICTED_OR_UNAPPROVED) + r')\b', re.IGNORECASE)
        if pattern.search(text):
            text = pattern.sub('approved bio-agents / KVK-verified formulation', text)
            safety_disclaimer = {
                'kn': "\n\n⚠️ [DPPQ&S ಸುರಕ್ಷತಾ ಎಚ್ಚರಿಕೆ]: ರಾಸಾಯನಿಕ ಕೀಟನಾಶಕಗಳ ಬದಲಿಗೆ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು (ಟ್ರೈಕೋಡರ್ಮಾ / ಬೇವಿನ ಎಣ್ಣೆ) ಬಳಸಿ ಅಥವಾ ಅನುಮೋದಿತ ಬಳಕೆಗೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆ ಸಂಪರ್ಕಿಸಿ.",
                'hi': "\n\n⚠️ [DPPQ&S सुरक्षा चेतावनी]: रासायनिक कीटनाशकों के स्थान पर जैविक नियंत्रण (ट्राइकोडर्मा / नीम तेल) अपनाएं या स्थानीय केवीके से परामर्श लें।",
                'en': "\n\n⚠️ [DPPQ&S Safety Warning]: Chemical pesticides must follow label-claim verification and CIB&RC regulations. Use approved bio-agents (Trichoderma / Pseudomonas / Neem oil 5%) or consult your local KVK."
            }.get(lang.lower(), "\n\n⚠️ [DPPQ&S Safety Warning]: Use approved bio-agents or consult your local KVK for verified treatments.")
            if "DPPQ&S" not in text:
                text += safety_disclaimer

        return text

    def ask_agronomist_rag(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        lang: str = "en",
        dashboard_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        res = self._ask_agronomist_rag_internal(query, chat_history, lang, dashboard_context)
        if res and isinstance(res, dict) and "answer" in res:
            res["answer"] = self.sanitize_llm_chemical_output(res["answer"], lang)
        return res

    def _ask_agronomist_rag_internal(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        lang: str = "en",
        dashboard_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main query processing pipeline:
        1. Multilingual Query Expansion + RAG Context Retrieval.
        2. Live LLM Generation with active Dashboard Agent Context.
        3. Domain Fallback Engine if LLM offline / rate limited / incomplete.
        """
        query_clean = query.strip()
        if not query_clean:
            empty_msg = {
                "kn": "ದಯವಿಟ್ಟು ಬೆಳೆಗಳು, ರಸಗೊಬ್ಬರಗಳು, ರೋಗಗಳು ಅಥವಾ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ.",
                "hi": "कृपया फसलों, उर्वरकों, रोगों या मंडी भाव के बारे में प्रश्न पूछें।",
                "en": "Please ask a question about crops, fertilizers, diseases, or market prices."
            }.get(lang, "Please ask a question about crops, fertilizers, diseases, or market prices.")
            return {"answer": empty_msg, "sources": [], "provider": self.provider_name}

        # Step 1: Retrieve relevant RAG context
        context_str, sources = agri_rag.get_rag_context_str(query_clean, top_k=3)

        lang_instructions = {
            "en": "Respond in clear, simple, farmer-friendly English. Avoid dense technical jargon. Use bullet points and practical field steps.",
            "hi": "Respond fluently in simple, conversational Hindi (हिन्दी). Use easy-to-understand terms that any village farmer can easily follow.",
            "kn": "Respond fluently in simple, conversational Kannada (ಕನ್ನಡ). Use friendly and clear agricultural terms for Karnataka farmers.",
            "te": "Respond fluently in simple Telugu (తెలుగు).",
            "mr": "Respond fluently in simple Marathi (मराठी)."
        }.get(lang.lower(), "Respond in clear, simple English.")

        # Format active dashboard context if present
        dashboard_text = ""
        if dashboard_context and isinstance(dashboard_context, dict):
            ctx_lines = []
            
            # Crop Recommendation Agent
            crop_ctx = dashboard_context.get('crop') or {}
            if crop_ctx.get('name') or crop_ctx.get('crop'):
                c_name = crop_ctx.get('name') or crop_ctx.get('crop')
                c_dist = crop_ctx.get('district') or crop_ctx.get('city') or 'Karnataka'
                c_season = crop_ctx.get('season') or 'Auto'
                c_weather = crop_ctx.get('weather') or ''
                c_adv = crop_ctx.get('advice') or ''
                ctx_lines.append(f"• [Crop Recommendation Agent]: Recommended Crop: '{c_name}' in District: {c_dist}, Season: {c_season}. Weather: {c_weather}. Agronomic advice: {c_adv}")

            # Market Price Agent
            price_ctx = dashboard_context.get('price') or {}
            if price_ctx.get('price') or price_ctx.get('predictedPrice') or price_ctx.get('priceText'):
                p_crop = price_ctx.get('crop') or price_ctx.get('priceCrop') or 'Selected Crop'
                p_dist = price_ctx.get('district') or price_ctx.get('city') or ''
                p_val = price_ctx.get('price') or price_ctx.get('predictedPrice') or price_ctx.get('priceText')
                p_txt = price_ctx.get('forecastText') or price_ctx.get('result') or ''
                ctx_lines.append(f"• [Market Price Forecast Agent]: Crop: '{p_crop}' in {p_dist}, Estimated Mandi Price: {p_val}. Forecast & Trend: {p_txt}")

            # Disease Detection Agent
            dis_ctx = dashboard_context.get('disease') or {}
            if dis_ctx.get('disease') or dis_ctx.get('predictedDisease'):
                d_crop = dis_ctx.get('crop') or 'Crop'
                d_name = dis_ctx.get('disease') or dis_ctx.get('predictedDisease')
                d_conf = dis_ctx.get('confidence') or 'N/A'
                d_res = dis_ctx.get('result') or ''
                ctx_lines.append(f"• [Plant Disease Detection Agent]: Plant: '{d_crop}', Diagnosed Condition: '{d_name}' (Confidence: {d_conf}). Cure Details: {d_res}")

            # Precision Irrigation Agent
            irri_ctx = dashboard_context.get('irrigation') or {}
            if irri_ctx.get('advice') or irri_ctx.get('crop') or irri_ctx.get('result'):
                i_crop = irri_ctx.get('crop') or 'Crop'
                i_stage = irri_ctx.get('stage') or irri_ctx.get('growth_stage') or 'Vegetative'
                i_soil = irri_ctx.get('soil') or irri_ctx.get('soil_type') or 'Loam'
                i_meth = irri_ctx.get('method') or irri_ctx.get('irrigation_type') or 'Drip'
                i_adv = irri_ctx.get('advice') or irri_ctx.get('result') or ''
                ctx_lines.append(f"• [Precision Irrigation Agent]: Crop: '{i_crop}', Growth Stage: {i_stage}, Soil: {i_soil}, Method: {i_meth}. Water Plan: {i_adv}")

            # Farm Planner Agent
            plan_ctx = dashboard_context.get('planner') or {}
            if plan_ctx.get('summary') or plan_ctx.get('ai_plan') or plan_ctx.get('alerts'):
                p_sum = plan_ctx.get('summary') or plan_ctx.get('ai_plan') or ''
                p_alt = plan_ctx.get('alerts') or ''
                p_prio = plan_ctx.get('priority') or ''
                ctx_lines.append(f"• [Complete Farm Planner Agent]: Integrated Plan Summary: {p_sum[:300]}... Urgent Alerts: {p_alt}. High Priority: {p_prio}")

            # Decision Intelligence Agent
            di_ctx = dashboard_context.get('decisionIntelligence') or {}
            if di_ctx.get('digitalTwin') or di_ctx.get('counterfactual') or di_ctx.get('debate'):
                ctx_lines.append("• [Decision Intelligence Agent]: Digital Twin, Counterfactual What-If, and Multi-Agent Consensus are active.")

            if ctx_lines:
                dashboard_text = "\n".join(ctx_lines)

        # Step 2: If live LLM is available, execute LangChain prompt
        if self.llm is not None and LANGCHAIN_AVAILABLE:
            try:
                system_prompt = (
                    "You are 'SmartAgri AI Agronomist', an expert agricultural AI assistant created to explain complex AI & ML farm predictions to Indian and Karnataka farmers in VERY SIMPLE, PLAIN, EASY-TO-UNDERSTAND language.\n\n"
                    "CORE MISSION FOR EXPLAINING AGENT RESULTS:\n"
                    "When the farmer asks you to explain the results, explain what an agent did, or asks about crop recommendation, market price, plant disease, irrigation, farm plan, or decision intelligence:\n"
                    "1. Explain in SIMPLE, EVERYDAY FARMER WORDS without confusing academic or technical terms.\n"
                    "2. Structure your explanation with clear, practical sections:\n"
                    "   • 🌾 **What this means for your farm (Simple Summary)**: In 1-2 easy sentences, explain the result clearly.\n"
                    "   • 🔍 **Why this was chosen (The Reason)**: Explain how the soil, weather, mandi demand, or symptoms led to this result.\n"
                    "   • 🚜 **What you should do on your field (Step-by-Step Action Plan)**: Give practical, exact instructions (dosages, timing, methods).\n"
                    "   • 💰 **How this helps your wallet & crop (Expected Benefit)**: Explain how much yield, water, or money they will save.\n"
                    "3. If the farmer asks about one specific agent (e.g. only Disease or only Market Price), focus on that agent while referencing the farm context.\n"
                    "4. Be encouraging, warm, polite, and helpful.\n"
                    f"5. Language requirement: {lang_instructions}\n\n"
                    f"--- ACTIVE DASHBOARD RESULTS FROM SPECIALIZED AGENTS ---\n{dashboard_text or 'No specific agent results submitted yet. Provide general domain expertise.'}\n"
                    "--------------------------------------------------------\n\n"
                    f"--- VERIFIED AGRICULTURAL KNOWLEDGE BASE CONTEXT ---\n{context_str or 'Standard ICAR/UAS agronomy guidelines apply.'}\n"
                    "----------------------------------------------------"
                )

                messages = [SystemMessage(content=system_prompt)]

                if chat_history:
                    for msg in chat_history[-4:]:
                        role = msg.get("role", "user")
                        text = msg.get("content", "")
                        if role == "user":
                            messages.append(HumanMessage(content=text))
                        elif role == "assistant":
                            messages.append(AIMessage(content=text))

                messages.append(HumanMessage(content=query_clean))

                try:
                    response = self.llm.invoke(messages)
                    raw_content = response.content if hasattr(response, "content") else str(response)
                    answer_text = self._extract_content(raw_content)
                    if answer_text and self._is_response_complete(answer_text):
                        return {
                            "answer": answer_text,
                            "sources": sources,
                            "provider": self.provider_name,
                            "has_rag_context": bool(context_str)
                        }
                except Exception as e_primary:
                    # Try failover models
                    alt_answer = self._try_gemini_fallback_models(messages)
                    if alt_answer:
                        return {
                            "answer": alt_answer,
                            "sources": sources,
                            "provider": self.provider_name,
                            "has_rag_context": bool(context_str)
                        }
                    print(f"[LLM Service] Notice: Live LLM quota/error ({e_primary}). Switching to SmartAgri Multilingual Agronomist Engine.")
            except Exception as e:
                print(f"[LLM Service] Error during LLM setup: {e}")

        # Step 3: High-Grade Multilingual Fallback Engine
        return self._generate_fallback_response(query_clean, context_str, sources, lang, dashboard_context)

    def _generate_fallback_response(
        self,
        query: str,
        context_str: str,
        sources: List[str],
        lang: str = "en",
        dashboard_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive domain-expert agricultural answer engine for Kannada, Hindi, and English.
        Covers Karnataka sowing seasons, crops, fertilizers, diseases, pest control, schemes, and market advice.
        """
        q_l = query.lower().strip()
        lang_code = lang.lower() if lang in ["kn", "hi", "en"] else "en"

        # -------------------------------------------------------------
        # 0. DASHBOARD RESULTS & AGENT EXPLANATIONS
        # -------------------------------------------------------------
        is_explain_query = any(w in q_l for w in ["explain", "summary", "dashboard", "agent", "results", "ವಿವರಿಸಿ", "ತಿಳಿಸಿ", "ಸಲಹೆ", "समझाएं", "परिणाम", "विवरण", "what should i do", "what did"])
        if is_explain_query and dashboard_context:
            crop_info = dashboard_context.get('crop') or {}
            price_info = dashboard_context.get('price') or {}
            disease_info = dashboard_context.get('disease') or {}
            irri_info = dashboard_context.get('irrigation') or {}
            plan_info = dashboard_context.get('planner') or {}

            rec_crop = crop_info.get('name') or crop_info.get('crop') or 'Recommended Crop'
            dis_name = disease_info.get('disease') or disease_info.get('predictedDisease') or 'None detected'
            pr_val = price_info.get('price') or price_info.get('predictedPrice') or price_info.get('priceText') or 'Market Normal'

            if lang_code == "kn":
                ans = (
                    f"🌾 **ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಅಗ್ರಿ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಫಲಿತಾಂಶಗಳ ಸರಳ ವಿವರಣೆ (ರೈತ ಮಿತ್ರರಿಗೆ)**:\n\n"
                    f"1. **🌱 ಬೆಳೆ ಶಿಫಾರಸು ಏಜೆಂಟ್ (Crop Recommendation)**:\n"
                    f"   • **ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ**: **{rec_crop}**\n"
                    f"   • **ಕಾರಣ**: ನಿಮ್ಮ ಜಿಲ್ಲೆಯ ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಷ್ (NPK) ಅಂಶಗಳಿಗೆ ಈ ಬೆಳೆ ಅತಿ ಹೆಚ್ಚು ಇಳುವರಿ ನೀಡುತ್ತದೆ.\n\n"
                    f"2. **💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮುನ್ಸೂಚನೆ (Market Price Forecast)**:\n"
                    f"   • **ಅಂದಾಜು ಮಾರುಕಟ್ಟೆ ಬೆಲೆ**: **{pr_val}**\n"
                    f"   • **ಸಲಹೆ**: ಕೊಯ್ಲಿನ ತಕ್ಷಣ ಮಾರಾಟ ಮಾಡದೆ, ಬೆಲೆ ಗರಿಷ್ಠ ಮಟ್ಟ ತಲುಪುವ ತಿಂಗಳಲ್ಲಿ ಮಾರಾಟ ಮಾಡಲು ಯೋಜಿಸಿ.\n\n"
                    f"3. **🩺 ಸಸ್ಯ ರೋಗ ಪತ್ತೆ ಏಜೆಂಟ್ (Disease Diagnosis)**:\n"
                    f"   • **ಪತ್ತೆಯಾದ ರೋಗ**: **{dis_name}**\n"
                    f"   • **ತಕ್ಷಣದ ಕ್ರಮ**: ಬೇವಿನ ಎಣ್ಣೆ (5 ಮಿ.ಲೀ/ಲೀ) ಅಥವಾ ಶಿಫಾರಸು ಮಾಡಿದ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಸಂಜೆ ಸಮಯದಲ್ಲಿ ಸಿಂಪಡಿಸಿ.\n\n"
                    f"4. **🚜 ರೈತರು ಕೈಗೊಳ್ಳಬೇಕಾದ ಮುಂದಿನ ಕ್ರಮಗಳು**:\n"
                    f"   • ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಬೀಜೋಪಚಾರ ಮಾಡಿ.\n"
                    f"   • ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿ ಅಳವಡಿಸಿ 40% ರಷ್ಟು ನೀರು ಮತ್ತು ವಿದ್ಯುತ್ ಉಳಿಸಿ."
                )
            elif lang_code == "hi":
                ans = (
                    f"🌾 **आपके स्मार्टएग्री डैशबोर्ड परिणामों का सरल विवरण (किसान भाइयों के लिए)**:\n\n"
                    f"1. **🌱 फसल सिफारिश एजेंट (Crop Recommendation)**:\n"
                    f"   • **सुझाई गई फसल**: **{rec_crop}**\n"
                    f"   • **कारण**: आपके जिले की मिट्टी और वर्तमान मौसम के अनुसार यह फसल सबसे अधिक पैदावार देगी।\n\n"
                    f"2. **💰 मंडी भाव पूर्वानुमान एजेंट (Market Price Forecast)**:\n"
                    f"   • **अनुमानित मंडी भाव**: **{pr_val}**\n"
                    f"   • **सलाह**: कटाई के तुरंत बाद बेचने के बजाय सही समय पर बेचकर अधिकतम लाभ कमाएं।\n\n"
                    f"3. **🩺 पौध रोग पहचान एजेंट (Disease Diagnosis)**:\n"
                    f"   • **पहचाना गया रोग**: **{dis_name}**\n"
                    f"   • **उपाय**: नीम का तेल (5ml/लीटर पानी) या जैविक फफूंदनाशक का छिड़काव करें।\n\n"
                    f"4. **🚜 आपके लिए तुरंत करने योग्य कार्य**:\n"
                    f"   • बुवाई से पहले बीजोपचार अवश्य करें।\n"
                    f"   • ड्रिप सिंचाई अपनाकर 40% तक पानी और खाद बचाएं।"
                )
            else:
                ans = (
                    f"🌾 **Simple Explanation of Your SmartAgri Dashboard Results**:\n\n"
                    f"1. **🌱 Crop Recommendation Agent**:\n"
                    f"   • **Suggested Crop**: **{rec_crop}**\n"
                    f"   • **Why**: Tailored to your soil's NPK nutrients and regional weather for maximum yield and resilience.\n\n"
                    f"2. **💰 Market Price Forecast Agent**:\n"
                    f"   • **Expected Mandi Price**: **{pr_val}**\n"
                    f"   • **Farmer Tip**: Monitor APMC mandi arrivals and consider staggered selling for higher margins.\n\n"
                    f"3. **🩺 Plant Disease Detection Agent**:\n"
                    f"   • **Status**: **{dis_name}**\n"
                    f"   • **Immediate Action**: Apply prophylactic bio-fungicide or neem oil spray (5ml/L) to prevent leaf damage.\n\n"
                    f"4. **🚜 Action Steps for Your Field**:\n"
                    f"   • Complete seed treatment before sowing.\n"
                    f"   • Use micro-irrigation (Drip) to save up to 45% water and boost fertilizer efficiency."
                )
            return {
                "answer": ans,
                "sources": ["[SmartAgri Dashboard Multi-Agent Synthesizer]"],
                "provider": "SmartAgri Explainer Engine"
            }

        # -------------------------------------------------------------
        # 1. DYNAMIC SEASONAL SOWING & BEST CROPS ADVISORY (MONTH & WEATHER AWARE)
        # -------------------------------------------------------------
        is_planner_prompt = any(w in q_l for w in ["lead ai agronomist", "360-degree farm management plan", "farm decision strategy", "executive decision & farm readiness"])
        is_seasonal_sowing_query = not is_planner_prompt and (
            any(w in q_l for w in [
                "ಜೂನ್", "ಮುಂಗಾರು", "ಖಾರಿಫ್", "ಬಿತ್ತನೆ", "ಹಿಂಗಾರು", "ರಬಿ", "ನವೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ಬೇಸಿಗೆ", 
                "june", "kharif", "rabi", "sowing", "monsoon", "winter", "november", "october", "summer", "zaid",
                "ಬುನ್ನಾಯಿ", "बुवाई", "जून", "खरीफ", "रबी", "नवंबर", "अक्टूबर", "मौसम"
            ])
            and any(w in q_l for w in [
                "ಬೆಳೆ", "ಬೆಳೆಗಳು", "ಯಾವುವು", "ಸೂಕ್ತ", "crop", "crops", "फसल", "ಫಸಲು", "suitable", "best", "plant", "recommend", "which crop", "what to grow"
            ])
        )

        if is_seasonal_sowing_query:
            ans = self._build_dynamic_seasonal_sowing_answer(q_l, lang_code, dashboard_context)
            return {
                "answer": ans,
                "sources": ["[ICAR Karnataka Agro-Climatic Crop Calendar Guide]"],
                "provider": "SmartAgri Multilingual Agronomist Engine",
                "has_rag_context": True
            }

        # -------------------------------------------------------------
        # 3. FERTILIZER & NPK DOSAGE ADVISORY (CROP & ACRE SPECIFIC)
        # -------------------------------------------------------------
        if any(w in q_l for w in ["ಗೊಬ್ಬರ", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "ರಸಗೊಬ್ಬರ", "ಖಾದ", "fertilizer", "fertilizers", "npk", "urea", "dap", "खाद", "उर्वरक", "यूरिया"]):
            is_mango = any(w in q_l for w in ["ಮಾವು", "ಮಾವಿನ", "ಮಾವಿನ ಮರ", "ಮಾವಿನ ಗಿಡ", "mango", "mangoes", "aam", "आम", "आम के", "आम का", "आम में"])
            is_tomato = any(w in q_l for w in ["ಟೊಮಾಟೊ", "ಟೊಮೆಟೊ", "ಟೊಮ್ಯಾಟೋ", "tomato", "tamatar", "टमाटर"])
            is_paddy = any(w in q_l for w in ["ಭತ್ತ", "ಅಕ್ಕಿ", "paddy", "rice", "dhan", "धान", "चावल"])
            is_maize = any(w in q_l for w in ["ಮೆಕ್ಕೆಜೋಳ", "ಮಕ್ಕಾ", "maize", "corn", "makka", "मक्का", "मक्के"])
            is_sugarcane = any(w in q_l for w in ["ಕಬ್ಬು", "ಕಬ್ಬಿನ", "sugarcane", "ganna", "गन्ना", "गन्ने"])
            is_cotton = any(w in q_l for w in ["ಹತ್ತಿ", "cotton", "kapas", "कपास"])
            is_banana = any(w in q_l for w in ["ಬಾಳೆ", "ಬಾಳೆಹಣ್ಣು", "banana", "kela", "केला", "केले"])

            if is_mango:
                if lang_code == "kn":
                    ans = (
                        "🥭 **ಮಾವಿನ ಮರಗಳಿಗೆ (Mango) ವೈಜ್ಞಾನಿಕ ರಸಗೊಬ್ಬರ (NPK) ಹಾಗೂ ಪೋಷಕಾಂಶ ನಿರ್ವಹಣಾ ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "ICAR-IIHR (ತೋಟಗಾರಿಕಾ ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ) ಶಿಫಾರಸಿನ ಪ್ರಕಾರ ಮಾವಿನ ಮರದ ವಯಸ್ಸಿಗೆ ಅನುಗುಣವಾಗಿ ರಸಗೊಬ್ಬರ ಒದಗಿಸಬೇಕು:\n\n"
                        "1. **ಸಾವಯವ ಗೊಬ್ಬರ (ಜುಲೈ–ಆಗಸ್ಟ್ / ಕಟಾವಿನ ನಂತರದ ಮಳೆಗಾಲದಲ್ಲಿ)**:\n"
                        "   • **1 ರಿಂದ 3 ವರ್ಷದ ಸಸಿಗಳಿಗೆ**: 10–15 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ + 500 ಗ್ರಾಂ ಬೇವಿನ ಹಿಂಡಿ ಪ್ರತಿ ಗಿಡಕ್ಕೆ.\n"
                        "   • **4 ರಿಂದ 9 ವರ್ಷದ ಮರಗಳಿಗೆ**: 25–40 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ + 1.5 ಕೆಜಿ ಬೇವಿನ ಹಿಂಡಿ.\n"
                        "   • **10 ವರ್ಷ ಮೇಲ್ಪಟ್ಟ ಪೂರ್ಣ ಫಲ ನೀಡುವ ಮರಗಳಿಗೆ**: 50–60 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ + 2 ಕೆಜಿ ಬೇವಿನ ಹಿಂಡಿ (ಕಾಂಡದಿಂದ 1.5–2 ಮೀಟರ್ ದೂರದಲ್ಲಿ ವೃತ್ತಾಕಾರದ ಪಾತಿಯಲ್ಲಿ ಹಾಕಿ).\n\n"
                        "2. **ರಾಸಾಯನಿಕ ರಸಗೊಬ್ಬರ (NPK) ಪ್ರಮಾಣ (ಪ್ರತಿ ಮರಕ್ಕೆ ಪ್ರತಿ ವರ್ಷ)**:\n"
                        "   • **1 ವರ್ಷದ ಸಸಿಗೆ**: 100 ಗ್ರಾಂ ಸಾರಜನಕ (N) : 50 ಗ್ರಾಂ ರಂಜಕ (P) : 100 ಗ್ರಾಂ ಪೊಟ್ಯಾಶ್ (K).\n"
                        "   • **2 ರಿಂದ 9 ವರ್ಷದವರೆಗೆ**: ಪ್ರತಿ ವರ್ಷಕ್ಕೆ 100 ಗ್ರಾಂ N, 50 ಗ್ರಾಂ P, 100 ಗ್ರಾಂ K ಪ್ರಮಾಣವನ್ನು ಹೆಚ್ಚಿಸುತ್ತಾ ಹೋಗಿ.\n"
                        "   • **10 ವರ್ಷ ಮೇಲ್ಪಟ್ಟ ಫಲ ನೀಡುವ ದೊಡ್ಡ ಮರಕ್ಕೆ**:\n"
                        "     - **ಸಾರಜನಕ (N)**: 1,000 ಗ್ರಾಂ (ಸುಮಾರು **2.2 ಕೆಜಿ ಯೂರಿಯಾ**)\n"
                        "     - **ರಂಜಕ (P)**: 500 ಗ್ರಾಂ (ಸುಮಾರು **3.1 ಕೆಜಿ ಸಿಂಗಲ್ ಸೂಪರ್ ಫಾಸ್ಫೇಟ್ - SSP**)\n"
                        "     - **ಪೊಟ್ಯಾಶ್ (K)**: 1,000 ಗ್ರಾಂ (ಸುಮಾರು **1.7 ಕೆಜಿ MOP ಪೊಟ್ಯಾಶ್**)\n\n"
                        "3. **ಗೊಬ್ಬರ ನೀಡುವ ಹಂತಗಳು ಮತ್ತು ಸಮಯ (2 ಕಂತುಗಳಲ್ಲಿ)**:\n"
                        "   • **1ನೇ ಕಂತು (ಜುಲೈ–ಆಗಸ್ಟ್ / ಕಟಾವಿನ ನಂತರ)**:\n"
                        "     - ಶೇ. 50 ರಷ್ಟು ಯೂರಿಯಾ (1.1 ಕೆಜಿ) + ಶೇ. 100 ರಷ್ಟು SSP (3.1 ಕೆಜಿ) + ಶೇ. 50 ರಷ್ಟು ಪೊಟ್ಯಾಶ್ (850 ಗ್ರಾಂ) ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರದೊಂದಿಗೆ ಹಾಕಿ. ಇದು ಹೊಸ ಚಿಗುರು ಬರಲು ಸಹಕಾರಿ.\n"
                        "   • **2ನೇ ಕಂತು (ಸೆಪ್ಟೆಂಬರ್–ಅಕ್ಟೋಬರ್ / ಹೂವು ಬಿಡುವ ಮುನ್ನ)**:\n"
                        "     - ಉಳಿದ ಶೇ. 50 ರಷ್ಟು ಯೂರಿಯಾ (1.1 ಕೆಜಿ) + ಶೇ. 50 ರಷ್ಟು ಪೊಟ್ಯಾಶ್ (850 ಗ್ರಾಂ) ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ ಲಘು ನೀರು ಹಾಯಿಸಿ.\n\n"
                        "4. **ಹೂವು ಮತ್ತು ಕಾಯಿ ಉದುರುವುದು ತಡೆಗಟ್ಟಲು ಸಿಂಪಡಣೆ**:\n"
                        "   • **ಹೂವು ಬಿಡುವ ಮುನ್ನ (ಅಕ್ಟೋಬರ್–ನವೆಂಬರ್)**: 13:0:45 (ಪೊಟ್ಯಾಶಿಯಂ ನೈಟ್ರೇಟ್) 10 ಗ್ರಾಂ/ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ (ಏಕರೂಪದ ಹೂಗೊಂಚಲು ಬರುತ್ತದೆ).\n"
                        "   • **ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ (ಬಟಾಣಿ ಗಾತ್ರ)**: ಬೋರಾಕ್ಸ್ (1.5 ಗ್ರಾಂ/ಲೀ) + ಜಿಂಕ್ ಸಲ್ಫೇಟ್ (2 ಗ್ರಾಂ/ಲೀ) + 0:0:50 (5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ ಕಾಯಿ ಉದುರುವುದು ನಿಲ್ಲಿಸಿ ಕಾಯಿ ಗಾತ್ರ ಮತ್ತು ರುಚಿ ಹೆಚ್ಚಿಸಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🥭 **आम (Mango) के बाग के लिए संतुलित खाद एवं उर्वरक (NPK) प्रबंधन सारणी**:\n\n"
                        "ICAR-IIHR (भारतीय बागवानी अनुसंधान संस्थान) की वैज्ञानिक सिफारिश के अनुसार आम के पेड़ की उम्र के अनुसार खाद दी जानी चाहिए:\n\n"
                        "1. **देसी व जैविक खाद (जुलाई–अगस्त / फल तुड़ाई के बाद)**:\n"
                        "   • **1 से 3 साल के पौधे**: 10-15 किग्रा सड़ी गोबर खाद + 500 ग्राम नीम की खली प्रति पौधा।\n"
                        "   • **4 से 9 साल के पेड़**: 25-40 किग्रा गोबर खाद + 1.5 किग्रा नीम की खली।\n"
                        "   • **10 वर्ष से अधिक के फलदार पेड़**: 50-60 किग्रा सड़ी गोबर की खाद + 2 किग्रा नीम की खली (तने से 1.5-2 मीटर दूर थाले/रिंग में डालें)।\n\n"
                        "2. **रासायनिक उर्वरक (NPK) की वार्षिक मात्रा (प्रति पेड़)**:\n"
                        "   • **1 वर्ष का पौधा**: 100 ग्राम नाइट्रोजन : 50 ग्राम फॉस्फोरस : 100 ग्राम पोटाश।\n"
                        "   • **2 से 9 वर्ष तक**: प्रति वर्ष 100g N, 50g P, 100g K बढ़ाते जाएं।\n"
                        "   • **10 वर्ष से बड़ा फलदार पेड़**:\n"
                        "     - **नाइट्रोजन (N)**: 1,000 ग्राम (लगभग **2.2 किग्रा यूरिया**)\n"
                        "     - **फॉस्फोरस (P)**: 500 ग्राम (लगभग **3.1 किग्रा SSP - सिंगल सुपर फॉस्फेट**)\n"
                        "     - **पोटाश (K)**: 1,000 ग्राम (लगभग **1.7 किग्रा MOP पोटाश**)\n\n"
                        "3. **उर्वरक देने का सही समय एवं विधि (2 किस्तों में)**:\n"
                        "   • **पहली खुराक (जुलाई–अगस्त)**: 50% यूरिया (1.1 किग्रा) + 100% SSP (3.1 किग्रा) + 50% पोटाश (850 ग्राम) गोबर खाद के साथ दें।\n"
                        "   • **दूसरी खुराक (सितंबर–अक्टूबर / बौर आने से पहले)**: शेष 50% यूरिया (1.1 किग्रा) + 50% पोटाश (850 ग्राम) डालकर हल्की सिंचाई करें।\n\n"
                        "4. **बौर (फूल) एवं फल झड़ने से रोकने हेतु छिड़काव**:\n"
                        "   • **बौर आने से पहले (अक्टूबर-नवंबर)**: पोटेशियम नाइट्रेट (13:0:45) @ 10 ग्राम/लीटर या 0:52:34 @ 5 ग्राम/लीटर का छिड़काव करें।\n"
                        "   • **फल मटर के दाने बराबर होने पर (फरवरी-मार्च)**: बोरेक्स @ 1.5 ग्राम/लीटर + जिंक सल्फेट @ 2 ग्राम/लीटर + 0:0:50 @ 5 ग्राम/लीटर का छिड़काव करें जिससे फल झड़ना बंद हो और फल का वजन व मिठास बढ़े।"
                    )
                else:
                    ans = (
                        "🥭 **Recommended Fertilizer & Nutrient Management Schedule for Mango (ಮಾವಿನ ಮರ / आम)**:\n\n"
                        "Based on ICAR-IIHR (Indian Institute of Horticultural Research) guidelines, mango tree fertilizer requirement depends on tree age and canopy spread:\n\n"
                        "1. **Organic Manure (Annual Application in July–August / Post-Harvest Monsoon)**:\n"
                        "   • **Young trees (1–3 years)**: 10–15 kg well-rotted FYM + 500g Neem Cake per tree.\n"
                        "   • **Growing trees (4–9 years)**: 25–40 kg FYM + 1.5 kg Neem Cake per tree.\n"
                        "   • **Mature bearing trees (10+ years)**: 50–60 kg FYM / Compost + 2 kg Neem Cake per tree applied in a circular basin/ring (1.5 to 2 meters away from the trunk).\n\n"
                        "2. **NPK Chemical Fertilizer Dosage (per Tree per Year)**:\n"
                        "   • **1-Year-Old Tree**: 100g N : 50g P₂O₅ : 100g K₂O\n"
                        "   • **2 to 9-Year-Old Trees**: Increase dosage annually by 100g N, 50g P, and 100g K per year of tree age.\n"
                        "   • **Mature Bearing Trees (10+ Years)**:\n"
                        "     - **Nitrogen (N)**: 1,000 g (approx. **2.2 kg Urea**)\n"
                        "     - **Phosphorus (P₂O₅)**: 500 g (approx. **3.1 kg Single Super Phosphate - SSP**)\n"
                        "     - **Potassium (K₂O)**: 1,000 g (approx. **1.7 kg Muriate of Potash - MOP**)\n\n"
                        "3. **Application Schedule & Timing (Split Applications)**:\n"
                        "   • **1st Split (July–August / Post-Harvest Monsoon)**:\n"
                        "     - Apply **50% Nitrogen (1.1 kg Urea) + 100% Phosphorus (3.1 kg SSP) + 50% Potassium (850g MOP)** along with FYM. This promotes vigorous new vegetative flush after harvesting.\n"
                        "   • **2nd Split (September–October / Pre-Flowering Differentiation)**:\n"
                        "     - Apply remaining **50% Nitrogen (1.1 kg Urea) + 50% Potassium (850g MOP)**. Incorporate into the soil ring and irrigate lightly.\n\n"
                        "4. **Foliar Sprays for Heavy Flowering, Fruit Retention & Quality**:\n"
                        "   • **Pre-Flowering (October–November)**: Spray **Potassium Nitrate (13:0:45) @ 10g/L** or **0:52:34 @ 5g/L** to induce uniform flower panicle emergence.\n"
                        "   • **Fruit Set Stage (Pea to Marble Size - Jan–Feb)**: Spray **Solubor / Boron @ 1.5g/L + Zinc Sulfate @ 2g/L + 0:0:50 (Potassium Sulfate) @ 5g/L** to stop fruit drop, improve fruit size, and enhance pulp sweetness.\n"
                        "   • **Alternate Bearing Control**: Apply **Paclobutrazol (Cultar)** @ 3–5 ml per meter canopy diameter in the soil collar during July–August for regular annual flowering."
                    )
                return {"answer": ans, "sources": ["[ICAR-IIHR Package of Practices for Mango]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_tomato:
                if lang_code == "kn":
                    ans = (
                        "🍅 **1 ಎಕರೆ ಟೊಮೆಟೊ (Tomato) ಬೆಳೆಗೆ ವೈಜ್ಞಾನಿಕ ರಸಗೊಬ್ಬರ (NPK) ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರದ ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "ಕರ್ನಾಟಕ ಕೃಷಿ ವಿಶ್ವವಿದ್ಯಾಲಯ (UASB / ICAR) ಶಿಫಾರಸಿನ ಪ್ರಕಾರ 1 ಎಕರೆ ಟೊಮೆಟೊ ಬೆಳೆಗೆ ಈ ಕೆಳಗಿನ ಪ್ರಮಾಣದಲ್ಲಿ ಗೊಬ್ಬರ ಒದಗಿಸಬೇಕು:\n\n"
                        "1. **ಸಾವಯವ ಗೊಬ್ಬರ (ಕೊನೆಯ ಉಳುಮೆಯಲ್ಲಿ)**:\n"
                        "   • **ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ / ಕಾಂಪೋಸ್ಟ್**: 10 ರಿಂದ 12 ಟನ್ (ಅಥವಾ 2 ಟನ್ ಎರೆಹುಳು ಗೊಬ್ಬರ).\n"
                        "   • **ಜೈವಿಕ ಗೊಬ್ಬರ**: ಟ್ರೈಕೋಡರ್ಮ (2 ಕೆಜಿ) + ಅಜೋಸ್ಪೈರಿಲಂ (2 ಕೆಜಿ) + ರಂಜಕ ಕರಗಿಸುವ ಪಿಎಸ್‌ಬಿ (2 ಕೆಜಿ) ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರದೊಂದಿಗೆ ಬೆರೆಸಿ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n\n"
                        "2. **ರಾಸಾಯನಿಕ ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ (1 ಎಕರೆಗೆ ಶುದ್ಧ NPK)**:\n"
                        "   • **ಸಾಮಾನ್ಯ ತಳಿಗಳಿಗೆ**: **45 ಕೆಜಿ ಸಾರಜನಕ (N) : 45 ಕೆಜಿ ರಂಜಕ (P) : 25 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ (K)**\n"
                        "   • **ಸಂಕೀರ್ಣ / ಹೈಬ್ರಿಡ್ ತಳಿಗಳಿಗೆ (ಉದಾ: ಸಾಹೋ, ಅಭಿನವ್, ಶಿವಮ್)**: **75 ಕೆಜಿ N : 60 ಕೆಜಿ P : 60 ಕೆಜಿ K**\n\n"
                        "3. **ರಸಗೊಬ್ಬರ ಚೀಲಗಳ ಲೆಕ್ಕಾಚಾರ ಮತ್ತು ನೀಡುವ ಸಮಯ (ವೇಳಾಪಟ್ಟಿ)**:\n"
                        "   • **ಮೂಲ ಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡುವಾಗ - Basal Dose)**:\n"
                        "     - ಡಿಎಪಿ (DAP): 100 ಕೆಜಿ (2 ಚೀಲ), ಅಥವಾ ಸಿಂಗಲ್ ಸೂಪರ್ ಫಾಸ್ಫೇಟ್ (SSP): 250 ಕೆಜಿ\n"
                        "     - ಎಂಒಪಿ (MOP - ಪೊಟ್ಯಾಶ್): 45-50 ಕೆಜಿ (1 ಚೀಲ)\n"
                        "     - ಯೂರಿಯಾ: 35 ಕೆಜಿ (1 ಚೀಲ)\n"
                        "     - ಜಿಂಕ್ ಸಲ್ಫೇಟ್: 10 ಕೆಜಿ + ಬೋರಾಕ್ಸ್: 4 ಕೆಜಿ\n"
                        "   • **1ನೇ ಮೇಲುಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡಿದ 30 ದಿನಗಳಿಗೆ / ಕವಲೊಡೆಯುವ ಹಂತ)**:\n"
                        "     - ಯೂರಿಯಾ: 35 ಕೆಜಿ\n"
                        "   • **2ನೇ ಮೇಲುಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡಿದ 45-50 ದಿನಗಳಿಗೆ / ಹೂ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ)**:\n"
                        "     - ಯೂರಿಯಾ: 30 ಕೆಜಿ + ಪೊಟ್ಯಾಶ್ (MOP): 20-25 ಕೆಜಿ\n\n"
                        "4. **ಹನಿ ನೀರಾವರಿ ಫರ್ಟಿಗೇಷನ್ (Drip Fertigation ಇದ್ದರೆ)**:\n"
                        "   • 19:19:19 (ಪ್ರತಿ ವಾರ 3-4 ಕೆಜಿ) ಬೆಳೆ ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ, ಮತ್ತು 13:0:45 ಹಾಗೂ 0:52:34 ಕಾಯಿ ಗಾತ್ರ ಹೆಚ್ಚಿಸಲು ನೀಡಿ.\n"
                        "   • **ಕ್ಯಾಲ್ಸಿಯಂ ನೈಟ್ರೇಟ್ (Calcium Nitrate)**: ಕಾಯಿ ಕೊಳೆ/ತೊಟ್ಟು ಕೊಳೆ (Blossom End Rot) ತಡೆಗಟ್ಟಲು ಕಾಯಿ ಕಟ್ಟುವಾಗ 5 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🍅 **1 एकड़ टमाटर की फसल के लिए संतुलित उर्वरक (NPK) एवं खाद प्रबंधन**:\n\n"
                        "1. **जैविक खाद (खेत की तैयारी के समय)**:\n"
                        "   • **सड़ी गोबर की खाद / कम्पोस्ट**: 10-12 टन प्रति एकड़ (या 2 टन वर्मीकम्पोस्ट)।\n"
                        "   • **जैव उर्वरक**: 2 किग्रा ट्राइकोडर्मा + 2 किग्रा पीएसबी को गोबर की खाद में मिलाकर खेत में डालें।\n\n"
                        "2. **अनुशंसित NPK खुराक (1 एकड़ हाइब्रिड टमाटर हेतु)**:\n"
                        "   • **नाइट्रोजन (N)**: 75 किग्रा | **फॉस्फोरस (P)**: 60 किग्रा | **पोटाश (K)**: 60 किग्रा\n\n"
                        "3. **उर्वरक देने की समय-सारणी (खाद की बोरियों के अनुसार)**:\n"
                        "   • **बुवाई/रोपाई के समय (बेसल डोज)**:\n"
                        "     - डीएपी (DAP): 100 किग्रा (2 बोरी)\n"
                        "     - पोटाश (MOP): 50 किग्रा (1 बोरी)\n"
                        "     - यूरिया: 35 किग्रा\n"
                        "     - जिंक सल्फेट: 10 किग्रा + बोरेक्स: 4 किग्रा\n"
                        "   • **पहली टॉप ड्रेसिंग (रोपाई के 30 दिन बाद)**: यूरिया 35 किग्रा/एकड़।\n"
                        "   • **दूसरी टॉप ड्रेसिंग (रोपाई के 50 दिन बाद / फूल-फल बनते समय)**: यूरिया 30 किग्रा + पोटाश 25 किग्रा।\n\n"
                        "💡 **टिप**: फल फटने और नीचे से काला होने (Blossom End Rot) से बचाने के लिए कैल्शियम नाइट्रेट 5 ग्राम/लीटर का छिड़काव करें।"
                    )
                else:
                    ans = (
                        "🍅 **Recommended Fertilizer & NPK Schedule for 1 Acre Tomato**:\n\n"
                        "1. **Organic Manure (Field Preparation)**:\n"
                        "   • **Well-rotted FYM / Compost**: 10–12 tonnes/acre (or 2 tonnes Vermicompost).\n"
                        "   • **Bio-agents**: 2 kg *Trichoderma viride* + 2 kg PSB mixed with farmyard manure.\n\n"
                        "2. **NPK Requirement (Hybrid Tomato per Acre)**:\n"
                        "   • **75 kg Nitrogen (N) : 60 kg Phosphorus (P2O5) : 60 kg Potassium (K2O)**\n\n"
                        "3. **Application Schedule (Fertilizer Bag Dosage)**:\n"
                        "   • **Basal Application (At Transplanting)**:\n"
                        "     - DAP: 100 kg (2 bags) OR Single Super Phosphate (SSP): 250 kg\n"
                        "     - MOP (Potash): 50 kg (1 bag)\n"
                        "     - Urea: 35 kg\n"
                        "     - Zinc Sulphate: 10 kg + Borax: 4 kg\n"
                        "   • **First Top Dressing (30 Days After Transplanting)**: Urea 35 kg/acre\n"
                        "   • **Second Top Dressing (45–50 DAT at Flowering/Fruiting)**: Urea 30 kg + MOP 25 kg/acre\n\n"
                        "💡 **Quality Tip**: Foliar spray Calcium Nitrate @ 5 g/L + Boron @ 1 g/L during fruit set to prevent Blossom End Rot."
                    )
                return {"answer": ans, "sources": ["[ICAR & UAS Package of Practices for Tomato]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_paddy:
                if lang_code == "kn":
                    ans = (
                        "🌾 **1 ಎಕರೆ ಭತ್ತಕ್ಕೆ (Paddy/Rice) ರಸಗೊಬ್ಬರ (NPK) ಮತ್ತು ಜಿಂಕ್ ನಿರ್ವಹಣಾ ಮಾರ್ಗದರ್ಶಿ**:\n\n"
                        "1. **ಶಿಫಾರಸು ಮಾಡಿದ NPK ಪ್ರಮಾಣ**: **40 ಕೆಜಿ ಸಾರಜನಕ (N) : 20 ಕೆಜಿ ರಂಜಕ (P) : 20 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ (K)** + 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್.\n\n"
                        "2. **ಚೀಲಗಳ ಲೆಕ್ಕ ಮತ್ತು ಕೊಡುವ ಸಮಯ**:\n"
                        "   • **ಮೂಲ ಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡುವಾಗ)**: DAP 45 ಕೆಜಿ (1 ಚೀಲ) + ಪೊಟ್ಯಾಶ್ (MOP) 18 ಕೆಜಿ + ಯೂರಿಯಾ 15 ಕೆಜಿ + ಜಿಂಕ್ ಸಲ್ಫೇಟ್ 10 ಕೆಜಿ.\n"
                        "   • **1ನೇ ಮೇಲುಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡಿದ 20–25 ದಿನಗಳಿಗೆ - ಕವಲೊಡೆಯುವಾಗ)**: ಯೂರಿಯಾ 35 ಕೆಜಿ.\n"
                        "   • **2ನೇ ಮೇಲುಗೊಬ್ಬರ (ನಾಟಿ ಮಾಡಿದ 45 ದಿನಗಳಿಗೆ - ತೆನೆ ಹೊಡೆಯುವ ಹಂತ)**: ಯೂರಿಯಾ 25 ಕೆಜಿ + MOP ಪೊಟ್ಯಾಶ್ 18 ಕೆಜಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🌾 **1 एकड़ धान (Paddy/Rice) के लिए अनुशंसित उर्वरक (NPK) प्रबंधन**:\n\n"
                        "1. **NPK की मात्रा**: **40 किग्रा नाइट्रोजन (N) : 20 किग्रा फॉस्फोरस (P) : 20 किग्रा पोटाश (K)** + 10 किग्रा जिंक सल्फेट।\n\n"
                        "2. **खाद देने की समय-सारणी**:\n"
                        "   • **रोपाई के समय (बेसल)**: DAP 45 किग्रा + MOP 18 किग्रा + यूरिया 15 किग्रा + जिंक सल्फेट 10 किग्रा।\n"
                        "   • **पहली टॉप ड्रेसिंग (20-25 दिन बाद - कल्ले फूटते समय)**: यूरिया 35 किग्रा/एकड़।\n"
                        "   • **दूसरी टॉप ड्रेसिंग (40-45 दिन बाद - बाली निकलने से पहले)**: यूरिया 25 किग्रा + पोटाश 18 किग्रा।"
                    )
                else:
                    ans = (
                        "🌾 **Recommended Fertilizer & NPK Schedule for 1 Acre Paddy/Rice**:\n\n"
                        "1. **Recommended NPK Dose**: **40 kg Nitrogen (N) : 20 kg Phosphorus (P₂O₅) : 20 kg Potassium (K₂O)** + 10 kg Zinc Sulfate.\n\n"
                        "2. **Fertilizer Bags & Application Timing**:\n"
                        "   • **Basal (At Transplanting)**: DAP 45 kg (1 bag) + MOP 18 kg + Urea 15 kg + Zinc Sulfate 10 kg.\n"
                        "   • **1st Top Dressing (20–25 DAT - Tillering Stage)**: Urea 35 kg/acre.\n"
                        "   • **2nd Top Dressing (40–45 DAT - Panicle Initiation)**: Urea 25 kg + MOP 18 kg/acre."
                    )
                return {"answer": ans, "sources": ["[ICAR & UAS Package of Practices for Rice]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_maize:
                if lang_code == "kn":
                    ans = (
                        "🌽 **1 ಎಕರೆ ಮೆಕ್ಕೆಜೋಳ (Maize) ಬೆಳೆಗೆ ಸಮಗ್ರ ರಸಗೊಬ್ಬರ (NPK) ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "1. **ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣ**: **48 ಕೆಜಿ ಸಾರಜನಕ (N) : 24 ಕೆಜಿ ರಂಜಕ (P) : 16 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ (K)**.\n\n"
                        "2. **ಗೊಬ್ಬರ ನೀಡುವ ಹಂತಗಳು**:\n"
                        "   • **ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ (ಬಾಸಲ್ ಡೋಸ್)**: DAP 50 ಕೆಜಿ (1 ಚೀಲ) + ಪೊಟ್ಯಾಶ್ (MOP) 25 ಕೆಜಿ + ಯೂರಿಯಾ 20 ಕೆಜಿ + ಜಿಂಕ್ ಸಲ್ಫೇಟ್ 10 ಕೆಜಿ.\n"
                        "   • **1ನೇ ಮೇಲುಗೊಬ್ಬರ (ಬಿತ್ತನೆಯ 30 ದಿನಗಳಿಗೆ - ಮೊಣಕಾಲು ಎತ್ತರದಲ್ಲಿ)**: ಯೂರಿಯಾ 40 ಕೆಜಿ.\n"
                        "   • **2ನೇ ಮೇಲುಗೊಬ್ಬರ (ಬಿತ್ತನೆಯ 50 ದಿನಗಳಿಗೆ - ಹೂ/ತೆನೆ ಮೂಡುವಾಗ)**: ಯೂರಿಯಾ 35 ಕೆಜಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🌽 **1 एकड़ मक्का (Maize) के लिए उर्वरक (NPK) सारणी**:\n\n"
                        "1. **अनुशंसित NPK खुराक**: **48 किग्रा N : 24 किग्रा P : 16 किग्रा K** प्रति एकड़।\n\n"
                        "2. **खाद देने का समय**:\n"
                        "   • **बुवाई के समय**: DAP 50 किग्रा + पोटाश 25 किग्रा + यूरिया 20 किग्रा + जिंक 10 किग्रा।\n"
                        "   • **पहली टॉप ड्रेसिंग (30 दिन - घुटने बराबर अवस्था)**: यूरिया 40 किग्रा/एकड़।\n"
                        "   • **दूसरी टॉप ड्रेसिंग (50 दिन - मंजरी/नर फूल आते समय)**: यूरिया 35 किग्रा/एकड़।"
                    )
                else:
                    ans = (
                        "🌽 **Recommended Fertilizer & NPK Schedule for 1 Acre Maize (Corn)**:\n\n"
                        "1. **Recommended NPK Dose**: **48 kg Nitrogen (N) : 24 kg Phosphorus (P₂O₅) : 16 kg Potassium (K₂O)**.\n\n"
                        "2. **Application Schedule**:\n"
                        "   • **Basal (At Sowing)**: DAP 50 kg (1 bag) + MOP 25 kg + Urea 20 kg + Zinc Sulfate 10 kg.\n"
                        "   • **1st Top Dressing (30 Days - Knee High Stage)**: Urea 40 kg/acre.\n"
                        "   • **2nd Top Dressing (50 Days - Tasseling Stage)**: Urea 35 kg/acre."
                    )
                return {"answer": ans, "sources": ["[ICAR Maize Production Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_sugarcane:
                if lang_code == "kn":
                    ans = (
                        "🎋 **1 ಎಕರೆ ಕಬ್ಬು (Sugarcane) ಬೆಳೆಗೆ ರಸಗೊಬ್ಬರ (NPK) ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "1. **ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣ**: **100 ಕೆಜಿ ಸಾರಜನಕ (N) : 40 ಕೆಜಿ ರಂಜಕ (P) : 50 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ (K)**.\n\n"
                        "2. **ಗೊಬ್ಬರ ಕೊಡುವ ಹಂತಗಳು**:\n"
                        "   • **ನಾಟಿ ಮಾಡುವಾಗ**: DAP 90 ಕೆಜಿ + MOP 40 ಕೆಜಿ + ಯೂರಿಯಾ 35 ಕೆಜಿ + 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್.\n"
                        "   • **ನಾಟಿಯ 45 ದಿನಗಳಿಗೆ (ಕವಲೊಡೆಯುವಾಗ)**: ಯೂರಿಯಾ 60 ಕೆಜಿ.\n"
                        "   • **ನಾಟಿಯ 90 ದಿನಗಳಿಗೆ**: ಯೂರಿಯಾ 60 ಕೆಜಿ + MOP 45 ಕೆಜಿ.\n"
                        "   • **ನಾಟಿಯ 120 ದಿನಗಳಿಗೆ (ಮಣ್ಣು ಏರಿಸುವಾಗ)**: ಯೂರಿಯಾ 60 ಕೆಜಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🎋 **1 एकड़ गन्ना (Sugarcane) के लिए संतुलित उर्वरक प्रबंधन**:\n\n"
                        "1. **अनुशंसित NPK**: **100 किग्रा N : 40 किग्रा P : 50 किग्रा K** प्रति एकड़।\n\n"
                        "2. **खाद देने की सारणी**:\n"
                        "   • **बुवाई के समय**: DAP 90 किग्रा + पोटाश 40 किग्रा + यूरिया 35 किग्रा + जिंक सल्फेट 10 किग्रा।\n"
                        "   • **45 दिन बाद**: यूरिया 60 किग्रा/एकड़।\n"
                        "   • **90 दिन बाद**: यूरिया 60 किग्रा + पोटाश 45 किग्रा।\n"
                        "   • **120 दिन बाद (मिट्टी चढ़ाते समय)**: यूरिया 60 किग्रा।"
                    )
                else:
                    ans = (
                        "🎋 **Recommended Fertilizer & NPK Schedule for 1 Acre Sugarcane**:\n\n"
                        "1. **Recommended NPK Dose**: **100 kg Nitrogen (N) : 40 kg Phosphorus (P₂O₅) : 50 kg Potassium (K₂O)**.\n\n"
                        "2. **Application Schedule**:\n"
                        "   • **Basal (At Planting)**: DAP 90 kg + MOP 40 kg + Urea 35 kg + Zinc Sulfate 10 kg.\n"
                        "   • **45 Days After Planting (Tillering)**: Urea 60 kg/acre.\n"
                        "   • **90 Days After Planting**: Urea 60 kg + MOP 45 kg/acre.\n"
                        "   • **120 Days (Earthing-up)**: Urea 60 kg/acre."
                    )
                return {"answer": ans, "sources": ["[ICAR-SBI Sugarcane Production Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_cotton:
                if lang_code == "kn":
                    ans = (
                        "🌱 **1 ಎಕರೆ ಹತ್ತಿ (Cotton) ಬೆಳೆಗೆ ಸಮಗ್ರ ರಸಗೊಬ್ಬರ (NPK) ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "1. **ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣ**: **60 ಕೆಜಿ ಸಾರಜನಕ (N) : 30 ಕೆಜಿ ರಂಜಕ (P) : 30 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ (K)**.\n\n"
                        "2. **ಗೊಬ್ಬರ ನೀಡುವ ಹಂತಗಳು**:\n"
                        "   • **ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ**: DAP 65 ಕೆಜಿ + MOP 25 ಕೆಜಿ + ಯೂರಿಯಾ 25 ಕೆಜಿ + ಜಿಂಕ್ 10 ಕೆಜಿ.\n"
                        "   • **ಬಿತ್ತನೆಯ 30–35 ದಿನಗಳಿಗೆ**: ಯೂರಿಯಾ 40 ಕೆಜಿ.\n"
                        "   • **ಬಿತ್ತನೆಯ 60 ದಿನಗಳಿಗೆ (ಹೂ ಮತ್ತು ಬೋಂಡು ಕಟ್ಟುವಾಗ)**: ಯೂರಿಯಾ 40 ಕೆಜಿ + MOP 25 ಕೆಜಿ.\n"
                        "   • **ಎಲೆ ಕೆಂಪಾಗುವುದು ತಡೆಗಟ್ಟಲು**: ಮೆಗ್ನೀಸಿಯಂ ಸಲ್ಫೇಟ್ (10 ಗ್ರಾಂ/ಲೀಟರ್) + 19:19:19 (5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🌱 **1 एकड़ कपास (Cotton) के लिए उर्वरक एवं NPK सारणी**:\n\n"
                        "1. **अनुशंसित NPK खुराक**: **60 किग्रा N : 30 किग्रा P : 30 किग्रा K** प्रति एकड़।\n\n"
                        "2. **खाद देने का समय**:\n"
                        "   • **बुवाई के समय**: DAP 65 किग्रा + पोटाश 25 किग्रा + यूरिया 25 किग्रा + जिंक 10 किग्रा।\n"
                        "   • **30-35 दिन बाद (शाखीय वृद्धि)**: यूरिया 40 किग्रा/एकड़।\n"
                        "   • **60 दिन बाद (फूल व टिंडे बनते समय)**: यूरिया 40 किग्रा + पोटाश 25 किग्रा।\n"
                        "   • **पत्तियां लाल होने से रोकने हेतु**: मैग्नीशियम सल्फेट (10 ग्राम/लीटर) का छिड़काव करें।"
                    )
                else:
                    ans = (
                        "🌱 **Recommended Fertilizer & NPK Schedule for 1 Acre Cotton**:\n\n"
                        "1. **Recommended NPK Dose**: **60 kg Nitrogen (N) : 30 kg Phosphorus (P₂O₅) : 30 kg Potassium (K₂O)**.\n\n"
                        "2. **Application Schedule**:\n"
                        "   • **Basal (At Sowing)**: DAP 65 kg + MOP 25 kg + Urea 25 kg + Zinc Sulfate 10 kg.\n"
                        "   • **30–35 Days (Vegetative Branching)**: Urea 40 kg/acre.\n"
                        "   • **60 Days (Square & Boll Formation)**: Urea 40 kg + MOP 25 kg/acre.\n"
                        "   • **Leaf Reddening Prevention**: Foliar spray Magnesium Sulfate @ 10g/L + 19:19:19 @ 5g/L."
                    )
                return {"answer": ans, "sources": ["[ICAR-CICR Cotton Production Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if is_banana:
                if lang_code == "kn":
                    ans = (
                        "🍌 **1 ಎಕರೆ ಬಾಳೆ (Banana - G9) ಬೆಳೆಗೆ ರಸಗೊಬ್ಬರ (NPK) ನಿರ್ವಹಣಾ ವೇಳಾಪಟ್ಟಿ**:\n\n"
                        "1. **ಪ್ರತಿ ಗಿಡಕ್ಕೆ ಒಟ್ಟು ರಸಗೊಬ್ಬರ**: **200 ಗ್ರಾಂ ಸಾರಜನಕ (N) : 50 ಗ್ರಾಂ ರಂಜಕ (P) : 300 ಗ್ರಾಂ ಪೊಟ್ಯಾಶ್ (K)**.\n\n"
                        "2. **ಗೊಬ್ಬರ ಕೊಡುವ ಹಂತಗಳು (ನಾಟಿ ಮಾಡಿದ ನಂತರ)**:\n"
                        "   • **ನಾಟಿ ಮಾಡುವಾಗ**: 10 ಕೆಜಿ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ + 200 ಗ್ರಾಂ SSP ರಂಜಕ + 50 ಗ್ರಾಂ ಯೂರಿಯಾ.\n"
                        "   • **ನಾಟಿಯ 30 ದಿನಗಳಿಗೆ**: ಯೂರಿಯಾ 100 ಗ್ರಾಂ + ಪೊಟ್ಯಾಶ್ (MOP) 100 ಗ್ರಾಂ.\n"
                        "   • **ನಾಟಿಯ 60 ಮತ್ತು 90 ದಿನಗಳಿಗೆ**: ಪ್ರತಿ ಗಿಡಕ್ಕೆ ಯೂರಿಯಾ 100 ಗ್ರಾಂ + MOP 150 ಗ್ರಾಂ.\n"
                        "   • **ಗೊನೆ ಬಿಡುವ ಹಂತದಲ್ಲಿ (150-180 ದಿನಗಳು)**: MOP ಪೊಟ್ಯಾಶ್ 150 ಗ್ರಾಂ (ಕಾಯಿ ದಪ್ಪ ಮತ್ತು ತೂಕ ಬರಲು)."
                    )
                elif lang_code == "hi":
                    ans = (
                        "🍌 **1 एकड़ केला (Banana - G9) के लिए उर्वरक एवं NPK सारणी**:\n\n"
                        "1. **प्रति पौधा कुल खुराक**: **200 ग्राम नाइट्रोजन : 50 ग्राम फॉस्फोरस : 300 ग्राम पोटाश**।\n\n"
                        "2. **खाद देने की समय-सारणी**:\n"
                        "   • **रोपाई के समय**: 10 किग्रा गोबर खाद + 200 ग्राम SSP + 50 ग्राम यूरिया।\n"
                        "   • **30 दिन बाद**: यूरिया 100 ग्राम + पोटाश 100 ग्राम प्रति पौधा।\n"
                        "   • **60 एवं 90 दिन बाद**: यूरिया 100 ग्राम + पोटाश 150 ग्राम।\n"
                        "   • **घहर (लॉन्ग) निकलते समय (150-180 दिन)**: पोटाश 150 ग्राम प्रति पौधा (फलों के आकार और वजन के लिए)।"
                    )
                else:
                    ans = (
                        "🍌 **Recommended Fertilizer & NPK Schedule for 1 Acre Banana (Grand Naine - G9)**:\n\n"
                        "1. **Total NPK Requirement per Plant**: **200g Nitrogen (N) : 50g Phosphorus (P₂O₅) : 300g Potassium (K₂O)**.\n\n"
                        "2. **Application Schedule (per Plant)**:\n"
                        "   • **At Planting**: 10 kg FYM + 200g SSP (full phosphorus) + 50g Urea.\n"
                        "   • **30 Days After Planting**: Urea 100g + MOP 100g.\n"
                        "   • **60 & 90 Days After Planting**: Urea 100g + MOP 150g.\n"
                        "   • **Bunch Emergence (Shooting stage at 150–180 days)**: MOP 150g per plant for maximum bunch weight and finger length."
                    )
                return {"answer": ans, "sources": ["[ICAR-NRCB Banana Production Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            if lang_code == "kn":
                ans = (
                    "🌿 **ಸ್ಮಾರ್ಟ್‌ಅಗ್ರಿ ಸಮಗ್ರ ರಸಗೊಬ್ಬರ (NPK) ನಿರ್ವಹಣಾ ಮಾರ್ಗದರ್ಶಿ**:\n\n"
                    "• **ಸಾರಜನಕ (Nitrogen - N)**: ಎಲೆಗಳ ಸಮೃದ್ಧ ಬೆಳವಣಿಗೆಗೆ ಸಹಕಾರಿ. ಇದನ್ನು 2 ರಿಂದ 3 ಕಂತುಗಳಲ್ಲಿ (ಬಿತ್ತನೆ ಸಮಯ + ಕವಲೊಡೆಯುವಾಗ) ನೀಡಿ.\n"
                    "• **ರಂಜಕ (Phosphorus - P)**: ಬೇರುಗಳ ಬಲವರ್ಧನೆಗೆ ಅತ್ಯಗತ್ಯ. ಶೇ. 100 ರಷ್ಟು ರಂಜಕವನ್ನು ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿಯೇ (ಬಾಸಲ್ ಡೋಸ್) ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n"
                    "• **ಪೊಟ್ಯಾಶ್ (Potassium - K)**: ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿ ಮತ್ತು ಧಾನ್ಯ/ಕಾಯಿಗಳ ತೂಕ ಹೆಚ್ಚಿಸಲು ಸಹಕಾರಿ.\n\n"
                    "📊 **ಪ್ರಮುಖ ಬೆಳೆಗಳಿಗೆ ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣ (ಪ್ರತಿ ಎಕರೆಗೆ)**:\n"
                    "- **ಟೊಮೆಟೊ**: 45:45:25 ಕೆಜಿ NPK (ಹೈಬ್ರಿಡ್‌ಗೆ 75:60:60 ಕೆಜಿ NPK) + 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್.\n"
                    "- **ಭತ್ತ**: 40:20:20 ಕೆಜಿ NPK + 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್.\n"
                    "- **ಮೆಕ್ಕೆಜೋಳ**: 48:24:16 ಕೆಜಿ NPK.\n"
                    "- **ಕಬ್ಬು**: 100:40:50 ಕೆಜಿ NPK.\n"
                    "- **ಹತ್ತಿ**: 60:30:30 ಕೆಜಿ NPK."
                )
            elif lang_code == "hi":
                ans = (
                    "🌿 **उर्वरक एवं संतुलित NPK प्रबंधन सलाह**:\n\n"
                    "• **नाइट्रोजन (N)**: पत्तियों की वृद्धि के लिए। इसे 2-3 खुराकों में विभाजित करके दें।\n"
                    "• **फॉस्फोरस (P)**: जड़ों के विकास के लिए। 100% बुवाई के समय बेसल डोज के रूप में दें।\n"
                    "• **पोटाश (K)**: रोग प्रतिरोधक क्षमता और दानों की चमक व वजन के लिए जरूरी है।\n\n"
                    "📊 **प्रमुख फसलों की अनुशंसित खुराक (प्रति एकड़)**:\n"
                    "- **टमाटर**: 75:60:60 किग्रा NPK + 10 किग्रा जिंक सल्फेट\n"
                    "- **धान**: 40:20:20 किग्रा NPK + 10 किग्रा जिंक सल्फेट\n"
                    "- **मक्का**: 48:24:16 किग्रा NPK\n"
                    "- **गन्ना**: 100:40:50 किग्रा NPK"
                )
            else:
                ans = (
                    "🌿 **Balanced Fertilizer & NPK Advisory**:\n\n"
                    "• **Nitrogen (N)**: Promotes vigorous vegetative foliage. Split into 2-3 applications.\n"
                    "• **Phosphorus (P)**: Crucial for early root proliferation. Apply 100% at sowing as basal dose.\n"
                    "• **Potassium (K)**: Enhances drought/disease resistance and fruit/grain quality.\n\n"
                    "📊 **Crop-Specific NPK Recommendation (per Acre)**:\n"
                    "- **Tomato**: 75:60:60 kg NPK + 10 kg Zinc Sulfate (Hybrid)\n"
                    "- **Paddy/Rice**: 40:20:20 kg NPK + 10 kg Zinc Sulfate\n"
                    "- **Maize**: 48:24:16 kg NPK\n"
                    "- **Sugarcane**: 100:40:50 kg NPK\n"
                    "- **Cotton**: 60:30:30 kg NPK"
                )
            return {"answer": ans, "sources": ["[ICAR Fertilizer Management Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 4. MAIZE FALL ARMYWORM & PEST CONTROL ADVISORY
        # -------------------------------------------------------------
        is_faw_query = any(w in q_l for w in [
            "ಸೈನಿಕ ಹುಳು", "ಸೈನಿಕ ಹುಳ", "ಸೈನಿಕ", "ಫಾಲ್ ಆರ್ಮಿವರ್ಮ್", "armyworm", "fall armyworm", "faw", "फॉल आर्मीवर्म", "आर्मीवर्म", "सैनिक कीट"
        ]) or (
            any(w in q_l for w in ["ಮೆಕ್ಕೆಜೋಳ", "ಮಕ್ಕಾ", "मक्का", "मक्के", "maize", "corn"]) and
            any(w in q_l for w in ["ಹುಳ", "ಹುಳು", "ಕೀಟ", "ನಿಯಂತ್ರಣ", "ಪರಿಹಾರ", "pest", "insect", "borer", "worm", "कीट", "इल्ली", "रोकथाम"])
        )

        if is_faw_query:
            if lang_code == "kn":
                ans = (
                    "🐛 **ಮೆಕ್ಕೆಜೋಳದ ಸೈನಿಕ ಹುಳು (Fall Armyworm - FAW) ಸಮಗ್ರ ನಿಯಂತ್ರಣ ಹಾಗೂ ಪರಿಹಾರಗಳು**:\n\n"
                    "ಮೆಕ್ಕೆಜೋಳದಲ್ಲಿ ಸುಳಿ ತಿನ್ನುವ ಸೈನಿಕ ಹುಳುವಿನ (*Spodoptera frugiperda*) ಹಾನಿ ತಡೆಗಟ್ಟಲು ಈ ಕೆಳಗಿನ ಹಂತ-ಹಂತದ ವೈಜ್ಞಾನಿಕ ಕ್ರಮಗಳನ್ನು ಕೈಗೊಳ್ಳಿ:\n\n"
                    "1. **ಜೈವಿಕ ಮತ್ತು ಪರಿಸರ ಸ್ನೇಹಿ ಕ್ರಮಗಳು (Biological & Cultural Control)**:\n"
                    "   • **ಲಿಂಗಾಕರ್ಷಕ ಬಲೆಗಳು (Pheromone Traps)**: ಎಕರೆಗೆ 5 ರಿಂದ 6 ಫೆರೊಮೊನ್ ಬಲೆಗಳನ್ನು ಅಳವಡಿಸಿ ಗಂಡು ಪತಂಗಗಳನ್ನು ಆಕರ್ಷಿಸಿ ನಾಶಪಡಿಸಿ.\n"
                    "   • **ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಣೆ**: ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ (10-15 ದಿನಗಳಲ್ಲಿ) 1500 ppm ಬೇವಿನ ಎಣ್ಣೆಯನ್ನು ಪ್ರತಿ ಲೀಟರ್ ನೀರಿಗೆ 3-5 ಮಿ.ಲೀ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ (ಮೊಟ್ಟೆ ಮತ್ತು ಸಣ್ಣ ಮರಿಹುಳು ನಾಶವಾಗುತ್ತವೆ).\n"
                    "   • **ಜೈವಿಕ ಶಿಲೀಂಧ್ರ**: ಮೆಟಾರೈಜಿಯಂ ಅನಿಸೊಪ್ಲಿಯೇ (*Metarhizium anisopliae*) ಅಥವಾ ಬ್ಯೂವೇರಿಯಾ ಬಸ್ಸಿಯಾನ 5 ಗ್ರಾಂ/ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸುಳಿಗೆ ಸಿಂಪಡಿಸಿ.\n\n"
                    "2. **ಅನುಮೋದಿತ ನಿರ್ವಹಣೆ (IPM Management)**:\n"
                    "   • ಜೈವಿಕ ಪರಾವಲಂಬಿ ಟ್ರೈಕೋಗ್ರಾಮ ಕಾರ್ಡ್ ಬಳಸಿ.\n"
                    "   • ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆ ಅಗತ್ಯವಿದ್ದರೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಅಥವಾ ಕೃಷಿ ಅಧಿಕಾರಿಯ ಅನುಮೋದನೆ ಪಡೆದು ಲೇಬಲ್ ಸೂಚನೆಯಂತೆ ಬಳಸಿ."
                )
            elif lang_code == "hi":
                ans = (
                    "🐛 **मक्के में फॉल आर्मीवर्म (सैनिक कीट) का समग्र नियंत्रण एवं उपचार**:\n\n"
                    "मक्के की फसल में सुंडी/सैनिक कीट (*Spodoptera frugiperda*) की रोकथाम हेतु वैज्ञानिक उपाय:\n\n"
                    "1. **जैविक एवं यांत्रिक उपाय**:\n"
                    "   • **फेरोमोन ट्रैप**: प्रति एकड़ 5-6 फेरोमोन ट्रैप लगाएं।\n"
                    "   • **नीम तेल**: प्रारंभिक अवस्था (10-15 दिन) में नीम का तेल 1500 ppm (3-5 मिली/लीटर) का छिड़काव करें।\n"
                    "   • **जैविक कीटनाशक**: मेटाराइजियम एनीसोप्ली (5 ग्राम/लीटर) का छिड़काव करें।\n\n"
                    "2. **समेकित कीट प्रबंधन (IPM)**:\n"
                    "   • ट्राइकोग्रामा अंड परजीवी कार्ड का उपयोग करें।\n"
                    "   • रासायनिक छिड़काव हेतु अपने नजदीकी केवीके (KVK) से सत्यापित दवा एवं खुराक की जानकारी लें।"
                )
            else:
                ans = (
                    "🐛 **Maize Fall Armyworm (FAW - *Spodoptera frugiperda*) Integrated Pest Management**:\n\n"
                    "1. **Biological & Cultural Control**:\n"
                    "   • **Pheromone Traps**: Install 5 to 6 traps per acre to capture male moths.\n"
                    "   • **Neem Oil**: Spray Neem Oil 1500 ppm @ 3-5 ml/L at early seedling stage (10-15 days).\n"
                    "   • **Bio-agent**: Foliar application of *Metarhizium anisopliae* or *Beauveria bassiana* @ 5 g/L.\n\n"
                    "2. **Approved IPM Management**:\n"
                    "   • Release *Trichogramma* egg parasitoids in early stages.\n"
                    "   • For chemical intervention, consult your local KVK or agricultural officer for label-claim verified treatments."
                )
            return {"answer": ans, "sources": ["[ICAR & CIMMYT Fall Armyworm Protocol]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 5. PEST, DISEASE & SPRAY ADVISORY
        # -------------------------------------------------------------
        if any(w in q_l for w in ["ರೋಗ", "ಕೀಟ", "ಬ್ಲಾಸ್ಟ್", "ಬೂಸ್ಟ್", "ಕೀಟನಾಶಕ", "ಔಷಧಿ", "disease", "pest", "spray", "blight", "blast", "fungicide", "कीट", "रोग", "दवा", "कीटनाशक"]):
            if lang_code == "kn":
                ans = (
                    "🩺 **ಬೆಳೆ ರೋಗ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಸಲಹಾ ಮಾರ್ಗದರ್ಶಿ**:\n\n"
                    "1. **ಜೈವಿಕ / ಸಾವಯವ ಚಿಕಿತ್ಸೆ (Organic Control)**:\n"
                    "   • ಬೇವಿನ ಎಣ್ಣೆ (Neem Oil 1500 ppm) 3 ರಿಂದ 5 ಮಿ.ಲೀ ಪ್ರತಿ ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ (ನುಸಿ, ಹೇನು ಮತ್ತು ಕಂಬಳಿ ಹುಳುಗಳಿಗೆ).\n"
                    "   • ಬೇರು ಕೊಳೆತ ಮತ್ತು ಸೊರಗು ರೋಗಕ್ಕೆ: ಟ್ರೈಕೋಡರ್ಮ ವಿರಿಡೆ 5 ಗ್ರಾಂ/ಲೀಟರ್ ಮಣ್ಣಿಗೆ ಹಾಕಿ.\n\n"
                    "2. **ಸಮಗ್ರ ರೋಗ ನಿರ್ವಹಣೆ (IPM Protocol)**:\n"
                    "   • ರೋಗಗ್ರಸ್ತ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ, ಗಾಳಿ-ಬೆಳಕು ಸಿಗುವಂತೆ ಗಿಡಗಳ ಅಂತರ ಕಾಪಾಡಿ.\n"
                    "   • ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆ ಅಗತ್ಯವಿದ್ದರೆ ಸ್ಥಳೀಯ ಕೆವಿಕೆ (KVK) ಶಿಫಾರಸು ಮಾಡಿದ ಲೇಬಲ್ ಕ್ಲೇಮ್ ಪರಿಶೀಲಿಸಿ ಬಳಸಿ."
                )
            elif lang_code == "hi":
                ans = (
                    "🩺 **फसल रोग एवं कीट नियंत्रण परामर्श**:\n\n"
                    "1. **जैविक उपचार (Organic)**:\n"
                    "   • नीम का तेल (1500 ppm @ 3-5 मिली/लीटर पानी) का छिड़काव करें।\n"
                    "   • जड़ सड़न एवं उकठा रोग के लिए: ट्राइकोडर्मा विरिडी (5 ग्राम/लीटर)।\n\n"
                    "2. **समेकित रोग प्रबंधन**:\n"
                    "   • रोगी पत्तियों को तोड़कर नष्ट करें एवं उचित जल निकासी रखें।\n"
                    "   • रासायनिक छिड़काव हेतु स्थानीय केवीके (KVK) से अनुशंसित उपचार प्राप्त करें।"
                )
            else:
                ans = (
                    "🩺 **Integrated Pest & Disease Management Advisory**:\n\n"
                    "1. **Organic / Biological Control**:\n"
                    "   • Spray Neem Oil (1500 ppm @ 3-5 ml/L) for sucking pests (Aphids, Thrips, Whiteflies).\n"
                    "   • Root rot / Wilt prevention: Soil application of *Trichoderma viride* (5g/L or 2.5 kg/ha with FYM).\n\n"
                    "2. **Integrated Disease Protocol**:\n"
                    "   • Prune and destroy diseased foliage; ensure good drainage and airflow.\n"
                    "   • For chemical sprays, check product label claims and consult your local KVK for approved fungicides."
                )
            return {"answer": ans, "sources": ["[Integrated Pest Management Protocol]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 5. GOVERNMENT SCHEMES & SUBSIDIES IN KARNATAKA
        # -------------------------------------------------------------
        if any(w in q_l for w in ["ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ", "ರೈತ ಸಿರಿ", "ಗಂಗಾ ಕಲ್ಯಾಣ", "ಕಿಸಾನ್", "scheme", "subsidy", "kisan", "pmfby", "योजना", "सब्सिडी"]):
            if lang_code == "kn":
                ans = (
                    "🏛 **ಕರ್ನಾಟಕ ರಾಜ್ಯ ಹಾಗೂ ಕೇಂದ್ರ ಸರ್ಕಾರದ ಪ್ರಮುಖ ಕೃಷಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸಬ್ಸಿಡಿಗಳು**:\n\n"
                    "1. **ರೈತ ಸಿರಿ ಯೋಜನೆ (Raitha Siri)**: ಸಿರಿಧಾನ್ಯ (ರಾಗಿ, ನವಣೆ, ಸಾಮೆ ಇತ್ಯಾದಿ) ಬೆಳೆಯುವ ರೈತರಿಗೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹10,000 ಪ್ರೋತ್ಸಾಹಧನ.\n"
                    "2. **ಗಂಗಾ ಕಲ್ಯಾಣ ಯೋಜನೆ (Ganga Kalyana)**: ಸಣ್ಣ, ಅತಿ ಸಣ್ಣ ಹಾಗೂ ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ರೈತರಿಗೆ ಉಚಿತ ಕೊಳವೆಬಾವಿ ಹಾಗೂ ನೀರಾವರಿ ಪಂಪ್‌ಸೆಟ್ ಸೌಲಭ್ಯ.\n"
                    "3. **ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ (Krishi Bhagya)**: ಕೃಷಿ ಹೊಂಡ (Farm Pond) ನಿರ್ಮಾಣ, ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ ಹಾಗೂ ಡೀಸೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗೆ ಶೇ. 80-90 ರಷ್ಟು ಸಬ್ಸಿಡಿ.\n"
                    "4. **ಪಿಎಂ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (PM-KISAN)**: ವರ್ಷಕ್ಕೆ ₹6,000 ನೇರ ಆರ್ಥಿಕ ನೆರವು (3 ಕಂತುಗಳಲ್ಲಿ).\n"
                    "5. **ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY)**: ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳಿಂದಾಗುವ ಬೆಳೆ ನಷ್ಟಕ್ಕೆ ಅತ್ಯಂತ ಕಡಿಮೆ ಪ್ರೀಮಿಯಂನಲ್ಲಿ (ಮುಂಗಾರು ಶೇ. 2%, ಹಿಂಗಾರು ಶೇ. 1.5%) ಬೆಳೆ ವಿಮೆ ಪರಿಹಾರ.\n"
                    "6. **ಹನಿ ನೀರಾವರಿ ಸಬ್ಸಿಡಿ (PMKSY)**: ಹನಿ/ತುಂತುರು ನೀರಾವರಿ ಘಟಕಕ್ಕೆ ಶೇ. 45 ರಿಂದ 90 ರವರೆಗೆ ಸಹಾಯಧನ."
                )
            elif lang_code == "hi":
                ans = (
                    "🏛 **कर्नाटक एवं केंद्र सरकार की प्रमुख कृषि योजनाएं एवं सब्सिडी**:\n\n"
                    "1. **पीएम-किसान (PM-KISAN)**: ₹6,000/वर्ष 3 समान किस्तों में प्रत्यक्ष बैंक खाते में।\n"
                    "2. **रैथा सिरी योजना (Raitha Siri)**: मोटे अनाज (मिलेट्स) उगाने वाले किसानों को ₹10,000 प्रति हेक्टेयर प्रोत्साहन राशि।\n"
                    "3. **गंगा कल्याण योजना (Ganga Kalyana)**: छोटे और सीमांत किसानों के लिए मुफ्त बोरवेल और सिंचाई सुविधा।\n"
                    "4. **कृषि भाग्य योजना (Krishi Bhagya)**: खेत तलाई (Farm Pond) और सिंचाई उपकरण पर 80-90% सब्सिडी।\n"
                    "5. **पीएम फसल बीमा योजना (PMFBY)**: प्राकृतिक आपदाओं से फसल नुकसान पर न्यूनतम प्रीमियम में पूर्ण सुरक्षा।"
                )
            else:
                ans = (
                    "🏛 **Key Government Agriculture Schemes & Subsidies in Karnataka**:\n\n"
                    "1. **Raitha Siri Scheme**: ₹10,000 per hectare direct incentive for cultivating millets (Ragi, Foxtail, Little millet).\n"
                    "2. **Ganga Kalyana Scheme**: Free borewell drilling and pump energization for SC/ST and small/marginal farmers.\n"
                    "3. **Krishi Bhagya Scheme**: 80% to 90% subsidy for construction of Farm Ponds with polythene lining and diesel pumps.\n"
                    "4. **PM-KISAN**: ₹6,000/year direct income support transferred in 3 equal installments.\n"
                    "5. **PMFBY (Crop Insurance)**: Comprehensive risk cover with ultra-low farmer premium (2% Kharif, 1.5% Rabi).\n"
                    "6. **Micro-Irrigation Subsidy (PMKSY)**: 45% to 90% subsidy on Drip and Sprinkler installation."
                )
            return {"answer": ans, "sources": ["[Karnataka Agriculture Department Guidelines]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 6. CROP IRRIGATION & WATERING INTERVALS
        # -------------------------------------------------------------
        is_irrigation_query = any(w in q_l for w in [
            "सिंचाई", "पानी देना", "अंतराल", "पानी", "कितने दिन", "सिंचाई का समय", "irrigation", "water", "watering", "interval", "schedule", "stage", "stages",
            "ನೀರಾವರಿ", "ನೀರು", "ಅವಧಿ", "ದಿನಗಳಿಗೊಮ್ಮೆ", "ಎಷ್ಟು ದಿನ", "ನೀರು ಹಾಯಿಸ"
        ])

        if is_irrigation_query:
            # Maize specific
            if any(w in q_l for w in ["मक्का", "मक्के", "maize", "corn", "ಮೆಕ್ಕೆಜೋಳ"]):
                if lang_code == "hi":
                    ans = (
                        "🌽 **मक्के की फसल में सिंचाई का सही अंतराल एवं जल प्रबंधन**:\n\n"
                        "मक्के की फसल में मिट्टी के प्रकार और मौसम के अनुसार सिंचाई का सही अंतराल निम्न प्रकार रखें:\n\n"
                        "1. **मिट्टी के प्रकार अनुसार सिंचाई अंतराल**:\n"
                        "   • **हल्की / बलुई दोमट मिट्टी**: हर **6 से 8 दिन** के अंतराल पर हल्की सिंचाई करें।\n"
                        "   • **भारी / काली दोमट मिट्टी**: हर **10 से 12 दिन** के अंतराल पर सिंचाई करें (मिट्टी में दरारें पड़ने से पहले पानी दें)।\n"
                        "   • **ग्रीष्मकालीन (गर्मी) मक्का**: हर **5 से 7 दिन** के अंतराल पर पानी दें।\n"
                        "   • **खरीफ (वर्षा) मक्का**: यदि 10-15 दिन तक बारिश न हो, तो जीवन रक्षक सिंचाई अवश्य दें।\n\n"
                        "2. **मक्के में सिंचाई की 4 सबसे महत्वपूर्ण (क्रांतिक) अवस्थाएं**:\n"
                        "   • **घुटने की ऊंचाई (Knee-high, 30-35 दिन)**: प्रारंभिक वानस्पतिक बढ़वार के लिए।\n"
                        "   • **नर मंजरी / टेसलिंग अवस्था (Tasseling, 45-50 दिन)**: *सबसे महत्वपूर्ण समय* (इस समय पानी की कमी से परागण रुक जाता है)।\n"
                        "   • **सिल्किंग / भुट्टा बनने की अवस्था (Silking, 60-65 दिन)**: भुट्टे में बालें व दाने बनने हेतु।\n"
                        "   • **दाना भराव / दूधिया अवस्था (Grain Filling, 75-80 दिन)**: दानों के अच्छे वजन व चमक के लिए।\n\n"
                        "💡 **विशेष कृषि सुझाव**:\n"
                        "• मक्के के खेत में जलभराव (Waterlogging) न होने दें, उचित जलनिकासी रखें।\n"
                        "• **ड्रिप सिंचाई**: ड्रिप सिंचाई से 40-50% पानी की बचत और 25% अधिक पैदावार मिलती है।"
                    )
                elif lang_code == "kn":
                    ans = (
                        "🌽 **ಮೆಕ್ಕೆಜೋಳದ ಬೆಳೆಗೆ ನೀರಾವರಿ ಅವಧಿ ಮತ್ತು ಸಮಗ್ರ ನಿರ್ವಹಣೆ**:\n\n"
                        "1. **ಮಣ್ಣಿನ ಪ್ರಕಾರಕ್ಕೆ ಅನುಗುಣವಾಗಿ ನೀರಾವರಿ ಅವಧಿ**:\n"
                        "   • **ಮರಳು ಮಿಶ್ರಿತ / ಕೆಂಪು ಮಣ್ಣು**: ಪ್ರತಿ **6 ರಿಂದ 8 ದಿನಗಳಿಗೊಮ್ಮೆ** ನೀರು ಹಾಯಿಸಿ.\n"
                        "   • **ಕಪ್ಪು / ಗೋಡು ಮಣ್ಣು**: ಪ್ರತಿ **10 ರಿಂದ 12 ದಿನಗಳಿಗೊಮ್ಮೆ** ನೀರಾವರಿ ಮಾಡಿ.\n"
                        "   • **ಬೇಸಿಗೆ ಮೆಕ್ಕೆಜೋಳ**: ತಾಪಮಾನ ಹೆಚ್ಚಿರುವುದರಿಂದ ಪ್ರತಿ **5 ರಿಂದ 7 ದಿನಗಳಿಗೊಮ್ಮೆ** ನೀರು ಒದಗಿಸಿ.\n"
                        "   • **ಮುಂಗಾರು ಬೆಳೆ**: ಮಳೆ ಕೈಕೊಟ್ಟಾಗ 10-12 ದಿನಕ್ಕೊಮ್ಮೆ ರಕ್ಷಕ ನೀರಾವರಿ ನೀಡಿ.\n\n"
                        "2. **ಮೆಕ್ಕೆಜೋಳದ 4 ಪ್ರಮುಖ ನೀರಾವರಿ ಹಂತಗಳು**:\n"
                        "   • **ಮೊಣಕಾಲು ಹಂತ (30-35 ದಿನಗಳು)**: ಗಿಡಗಳ ಶೀಘ್ರ ಬೆಳವಣಿಗೆಗೆ.\n"
                        "   • **ತೆನೆ / ಹೂಬಿಡುವ ಹಂತ (ಟ್ಯಾಸೆಲಿಂಗ್ 45-50 ದಿನಗಳು)**: ಅತ್ಯಂತ ಸೂಕ್ಷ್ಮ ಹಂತ (ಈ ಸಮಯದಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ).\n"
                        "   • **ರೇಷ್ಮೆ ಕುಚ್ಚು ಬರುವ ಹಂತ (ಸಿಲ್ಕಿಂಗ್ 60-65 ದಿನಗಳು)**: ಕಾಳು ಕಟ್ಟಲು.\n"
                        "   • **ಹಾಲು ತುಂಬುವ ಹಂತ (75-80 ದಿನಗಳು)**: ಕಾಳುಗಳ ತೂಕ ಹೆಚ್ಚಿಸಲು.\n\n"
                        "💡 **ಕೃಷಿ ಸಲಹೆ**: ಮೆಕ್ಕೆಜೋಳದ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ಇರಲಿ."
                    )
                else:
                    ans = (
                        "🌽 **Maize (Corn) Crop Irrigation Schedule & Water Management**:\n\n"
                        "1. **Irrigation Intervals by Soil & Season**:\n"
                        "   • **Sandy / Light Loam Soils**: Irrigate every **6 to 8 days**.\n"
                        "   • **Heavy Black / Clayey Soils**: Irrigate every **10 to 12 days**.\n"
                        "   • **Summer Crop**: Irrigate every **5 to 7 days** due to high evapotranspiration.\n"
                        "   • **Kharif (Monsoon)**: Provide supplemental irrigation during 10-15 day dry spells.\n\n"
                        "2. **4 Critical Irrigation Stages for Maize**:\n"
                        "   • **Knee-High Stage (30 - 35 days)**: For vigorous vegetative growth.\n"
                        "   • **Tasseling Stage (45 - 50 days)**: *Most critical stage* (water deficit halts pollination).\n"
                        "   • **Silking Stage (60 - 65 days)**: For cob formation and silk emergence.\n"
                        "   • **Grain Filling / Milking Stage (75 - 80 days)**: Enhances grain weight and starch content.\n\n"
                        "💡 **Agronomist Tip**: Avoid standing waterlogged conditions; ensure efficient field drainage."
                    )
                return {"answer": ans, "sources": ["[FAO & ICAR Irrigation Management Guide]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

            # General crop irrigation
            if lang_code == "hi":
                ans = (
                    "💧 **फसल सिंचाई अंतराल एवं जल प्रबंधन दिशानिर्देश**:\n\n"
                    "• **बलुई/हल्की मिट्टी**: हर 5 से 7 दिन के अंतराल पर हल्की सिंचाई करें।\n"
                    "• **दोमट/काली मिट्टी**: हर 8 से 12 दिन के अंतराल पर सिंचाई करें।\n"
                    "• **नाजुक अवस्थाएं**: कल्ले फूटते समय, फूल आते समय तथा दाना/फल बनते समय खेत में नमी अवश्य बनाए रखें।\n"
                    "• **आधुनिक तकनीक**: ड्रिप सिंचाई प्रणाली अपनाएं जिससे 40-50% पानी की बचत होती है।"
                )
            elif lang_code == "kn":
                ans = (
                    "💧 **ಬೆಳೆಗಳ ನೀರಾವರಿ ಅವಧಿ ಮತ್ತು ನಿರ್ವಹಣಾ ಮಾರ್ಗದರ್ಶಿ**:\n\n"
                    "• **ಮರಳು/ಕೆಂಪು ಮಣ್ಣು**: ಪ್ರತಿ 5 ರಿಂದ 7 ದಿನಗಳಿಗೊಮ್ಮೆ ನೀರು ಹಾಯಿಸಿ.\n"
                    "• **ಕಪ್ಪು/ಗೋಡು ಮಣ್ಣು**: ಪ್ರತಿ 8 ರಿಂದ 12 ದಿನಗಳಿಗೊಮ್ಮೆ ನೀರಾವರಿ ಮಾಡಿ.\n"
                    "• **ಪ್ರಮುಖ ಹಂತಗಳು**: ಕವಲೊಡೆಯುವಾಗ, ಹೂವು ಬಿಡುವಾಗ ಹಾಗೂ ಕಾಳು ಕಟ್ಟುವಾಗ ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಅತ್ಯಗತ್ಯ.\n"
                    "• **ಹನಿ ನೀರಾವರಿ**: ಹನಿ ನೀರಾವರಿ ಅಳವಡಿಸಿ ಶೇ. 45-50 ರಷ್ಟು ನೀರನ್ನು ಉಳಿಸಿ."
                )
            else:
                ans = (
                    "💧 **Crop Irrigation Interval & Water Management Guidelines**:\n\n"
                    "• **Light Sandy Soil**: Irrigate every 5 to 7 days.\n"
                    "• **Heavy Loamy/Black Soil**: Irrigate every 8 to 12 days.\n"
                    "• **Critical Growth Stages**: Maintain adequate moisture at Tillering, Flowering, and Fruit/Grain filling.\n"
                    "• **Drip Irrigation**: Recommended for 40-50% water savings and enhanced crop yield."
                )
            return {"answer": ans, "sources": ["[SmartAgri Smart Irrigation Engine]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 6. GENERAL CONTEXTUAL RAG FALLBACK (STRICTLY RESPECT LANGUAGE)
        # -------------------------------------------------------------
        if context_str:
            if lang_code == "kn":
                ans = (
                    f"🌾 **ಸ್ಮಾರ್ಟ್‌ಅಗ್ರಿ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆ ('{query}')**:\n\n"
                    "• **ಬೆಳೆ ನಿರ್ವಹಣೆ ಮತ್ತು ರಕ್ಷಣೆ**: ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಹಾಗೂ ಬೀಜೋಪಚಾರ (ಟ್ರೈಕೋಡರ್ಮ 4 ಗ್ರಾಂ/ಕೆಜಿ) ಮಾಡಿ.\n"
                    "• **ರಸಗೊಬ್ಬರ (NPK) ಬಳಕೆ**: ಶಿಫಾರಸು ಮಾಡಿದ ರಸಗೊಬ್ಬರವನ್ನು ಅಡಿಗೊಬ್ಬರ ಮತ್ತು ಮೇಲುಗೊಬ್ಬರವಾಗಿ ಹಂತ-ಹಂತವಾಗಿ ನೀಡಿ.\n"
                    "• **ಕೀಟ ಮತ್ತು ರೋಗ ತಡೆಗಟ್ಟುವಿಕೆ**: ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ ಬೇವಿನ ಎಣ್ಣೆ (3-5 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ; ಕೀಟ ಹಾನಿ ತೀವ್ರವಾಗಿದ್ದರೆ ಸೂಕ್ತ ಕೀಟನಾಶಕವನ್ನು ಸುಳಿಗೆ ಸಿಂಪಡಿಸಿ.\n"
                    "• **ವೈಜ್ಞಾನಿಕ ನೀರಾವರಿ**: ಹೂಬಿಡುವ ಹಾಗೂ ಕಾಳು ಕಟ್ಟುವ ನಿರ್ಣಾಯಕ ಹಂತಗಳಲ್ಲಿ ಸಮರ್ಪಕ ತೇವಾಂಶ ಕಾಪಾಡಿ.\n\n"
                    "💡 *ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಇನ್ನಷ್ಟು ನಿರ್ದಿಷ್ಟ ಮಾಹಿತಿ ಪಡೆಯಲು ಬೆಳೆಯ ಹೆಸರು, ವಯಸ್ಸು ಅಥವಾ ಜಿಲ್ಲೆಯನ್ನು ನಮೂದಿಸಿ.*"
                )
            elif lang_code == "hi":
                ans = (
                    f"🌾 **स्मार्टएग्री कृषि विशेषज्ञ सलाह ('{query}')**:\n\n"
                    "• **फसल सुरक्षा एवं पोषण**: बुवाई से पहले बीजोपचार (ट्राइकोडर्मा 4 ग्राम/किग्रा) अवश्य करें।\n"
                    "• **संतुलित उर्वरक**: मिट्टी परीक्षण अनुसार NPK उर्वरकों का प्रयोग सही समय (बेसल व टॉप ड्रेसिंग) पर करें।\n"
                    "• **कीट एवं रोग नियंत्रण**: प्रारंभिक अवस्था में नीम का तेल (3-5 मिली/लीटर) छिड़कें; प्रकोप होने पर अनुशंसित कीटनाशक का प्रयोग करें।\n"
                    "• **सिंचाई प्रबंधन**: फसल के महत्वपूर्ण चरणों (फूल व दाना बनते समय) पर्याप्त नमी बनाए रखें।\n\n"
                    "💡 *सटीक सलाह के लिए अपनी फसल, उम्र अथवा जिले का नाम बताएं।*"
                )
            else:
                ans = f"🌾 **SmartAgri Verified Agronomist Advisory**:\n\nBased on agricultural guidelines for your query:\n\n{context_str}"

            return {"answer": ans, "sources": sources or ["[ICAR Knowledge Base]"], "provider": "SmartAgri Multilingual Agronomist Engine", "has_rag_context": True}

        # -------------------------------------------------------------
        # 7. DEFAULT FRIENDLY ADVICE
        # -------------------------------------------------------------
        if lang_code == "kn":
            ans = (
                f"🌾 **ಸ್ಮಾರ್ಟ್‌ಅಗ್ರಿ ಕೃಷಿ ಸಲಹೆಗಾರರು ('{query}')**:\n\n"
                "• **ಮಣ್ಣು ಪರೀಕ್ಷೆ**: ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ ಶಿಫಾರಸು ಮಾಡಿದಂತೆ ರಸಗೊಬ್ಬರ (NPK) ಬಳಸಿ.\n"
                "• **ಬೀಜೋಪಚಾರ**: ಶಿಲೀಂಧ್ರ ಮತ್ತು ಬೇರು ರೋಗ ತಡೆಯಲು ಟ್ರೈಕೋಡರ್ಮ ವಿರಿಡೆ (4 ಗ್ರಾಂ/ಕೆಜಿ) ಮಿಶ್ರಣ ಮಾಡಿ.\n"
                "• **ನೀರಾವರಿ**: ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿ ಅಳವಡಿಸಿ ಶೇ. 40-50 ರಷ್ಟು ನೀರು ಉಳಿಸಿ.\n"
                "💡 *ಹೆಚ್ಚಿನ ವಿವರವಾದ ಸಲಹೆಗಾಗಿ ನಿಮ್ಮ ಬೆಳೆಯ ಹೆಸರು, ಜಿಲ್ಲೆ ಅಥವಾ ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ತಿಳಿಸಿ.*"
            )
        elif lang_code == "hi":
            ans = (
                f"🌾 **स्मार्टएग्री कृषि परामर्श ('{query}')**:\n\n"
                "• **मृदा परीक्षण**: बुवाई से पूर्व मिट्टी की जांच करवाएं और संतुलित NPK उर्वरकों का प्रयोग करें।\n"
                "• **बीजोपचार**: फफूंद जनित रोगों से सुरक्षा के लिए ट्राइकोडर्मा (4 ग्राम/किग्रा) से बीजोपचार करें।\n"
                "• **सिंचाई**: ड्रिप सिंचाई का उपयोग कर पानी की बचत करें।\n"
                "💡 *सटीक सलाह के लिए अपनी फसल का नाम, जिला अथवा मिट्टी का प्रकार बताएं।*"
            )
        else:
            ans = (
                f"🌾 **SmartAgri Agronomist Advisory for '{query}'**:\n\n"
                "• **Soil Health**: Conduct periodic soil testing and apply balanced NPK nutrients based on recommendations.\n"
                "• **Seed Treatment**: Treat seeds with *Trichoderma viride* (4g/kg) or *Pseudomonas* before planting.\n"
                "• **Irrigation**: Adopt micro-irrigation (Drip/Sprinkler) for up to 40% water savings and enhanced yield.\n"
                "💡 *For personalized guidance, please specify your crop name, soil type, or Karnataka district.*"
            )

        return {
            "answer": ans,
            "sources": sources or ["[SmartAgri Agricultural System]"],
            "provider": "SmartAgri Multilingual Agronomist Engine",
            "has_rag_context": False
        }

    def explain_crop_recommendation(
        self,
        crop: str,
        n: float,
        p: float,
        k: float,
        temp: float,
        humidity: float,
        ph: float,
        rainfall: float,
        lang: str = "en"
    ) -> str:
        """Generates an explanation for why a specific crop was recommended."""
        prompt = (
            f"A farmer input the following soil and environmental data:\n"
            f"- Nitrogen: {n}, Phosphorus: {p}, Potassium: {k}\n"
            f"- Temperature: {temp}°C, Humidity: {humidity}%, Soil pH: {ph}, Rainfall: {rainfall} mm\n\n"
            f"The Machine Learning model recommended: **{crop}**.\n\n"
            f"Please write a short (3-4 bullet points) agronomist explanation:\n"
            f"1. Why {crop} is scientifically well-suited for these soil NPK and climate conditions.\n"
            f"2. Practical soil preparation & sowing advice.\n"
            f"3. Key precaution for water or pest management.\n"
            f"Keep it encouraging, concise, and easy to understand. Respond in language: {lang}."
        )
        res = self.ask_agronomist_rag(prompt, lang=lang)
        return res.get("answer", "")

    def explain_disease_diagnosis(
        self,
        disease_name: str,
        confidence: float,
        lang: str = "en"
    ) -> str:
        """Generates an immediate treatment roadmap for a diagnosed leaf disease."""
        prompt = (
            f"A leaf photo was scanned by our Deep Learning CNN model and identified as: **{disease_name}** "
            f"with confidence: {confidence * 100:.1f}%.\n\n"
            f"Please provide an immediate action plan for the farmer:\n"
            f"1. Symptoms & Risk severity.\n"
            f"2. Organic / Biological treatment (e.g. Neem oil, Trichoderma).\n"
            f"3. Fast-acting Chemical fungicide/pesticide dosage (e.g. Mancozeb, Copper Oxychloride, etc.).\n"
            f"4. Preventive measures for surrounding healthy plants.\n"
            f"Keep it clear and actionable. Respond in language: {lang}."
        )
        res = self.ask_agronomist_rag(prompt, lang=lang)
        return res.get("answer", "")

    def _build_dynamic_seasonal_sowing_answer(
        self,
        q_l: str,
        lang_code: str,
        dashboard_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Dynamically generates seasonal sowing recommendations for Karnataka based on
        the active calendar month (e.g. November Rabi vs June Kharif) and agro-climatic zone.
        """
        now = datetime.now()
        month = now.month

        # Detect if query explicitly asks for a specific month
        if any(w in q_l for w in ["june", "jun", "ಜೂನ್", "जून"]):
            month = 6
        elif any(w in q_l for w in ["july", "jul", "ಜುಲೈ", "जुलाई"]):
            month = 7
        elif any(w in q_l for w in ["august", "aug", "ಆಗಸ್ಟ್", "अगस्त"]):
            month = 8
        elif any(w in q_l for w in ["september", "sep", "ಸೆಪ್ಟೆಂಬರ್", "सितंबर"]):
            month = 9
        elif any(w in q_l for w in ["october", "oct", "ಅಕ್ಟೋಬರ್", "अक्टूबर"]):
            month = 10
        elif any(w in q_l for w in ["november", "nov", "ನವೆಂಬರ್", "नवंबर"]):
            month = 11
        elif any(w in q_l for w in ["december", "dec", "ಡಿಸೆಂಬರ್", "दिसंबर"]):
            month = 12
        elif any(w in q_l for w in ["january", "jan", "ಜನವರಿ", "जनवरी"]):
            month = 1
        elif any(w in q_l for w in ["february", "feb", "ಫೆಬ್ರವರಿ", "फरवरी"]):
            month = 2
        elif any(w in q_l for w in ["march", "mar", "ಮಾರ್ಚ್", "मार्च"]):
            month = 3
        elif any(w in q_l for w in ["april", "apr", "ಏಪ್ರಿಲ್", "अप्रैल"]):
            month = 4
        elif any(w in q_l for w in ["may", "ಮೇ", "मई"]):
            month = 5
        elif any(w in q_l for w in ["kharif", "ಮುಂಗಾರು", "खरीफ", "monsoon"]):
            month = 6
        elif any(w in q_l for w in ["rabi", "ಹಿಂಗಾರು", "रबी", "winter"]):
            month = 11
        elif any(w in q_l for w in ["summer", "ಬೇಸಿಗೆ", "जायद", "zaid"]):
            month = 3

        # Extract active district if present in context
        crop_info = (dashboard_context.get('crop') or {}) if dashboard_context else {}
        active_dist = crop_info.get('city') or 'Karnataka'

        if month in [10, 11, 12, 1, 2]:
            # RABI (COOL / WINTER SEASON) - CURRENT ACTIVE SEASON IN NOVEMBER
            if lang_code == "kn":
                return (
                    "🌾 **ಕರ್ನಾಟಕದಲ್ಲಿ ನವೆಂಬರ್ ತಿಂಗಳಲ್ಲಿ (ಹಿಂಗಾರು / ರಬಿ ಹಂಗಾಮು) ಬಿತ್ತನೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತವಾದ ಪ್ರಮುಖ ಬೆಳೆಗಳು**:\n\n"
                    "ನವೆಂಬರ್ ತಿಂಗಳಲ್ಲಿ ಹಿಂಗಾರು ಚಳಿಗಾಲದ ಆರಂಭವಾಗುವುದರಿಂದ (ರಾತ್ರಿ ವೇಳೆ 16–20°C ತಂಪಾದ ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ತೇವಾಂಶಕ್ಕೆ) ಕರ್ನಾಟಕದ ಕಪ್ಪು ಹಾಗೂ ಗೋಡು ಮಣ್ಣಿನ ಜಿಲ್ಲೆಗಳಿಗೆ (ಬೀದರ್, ಕಲಬುರಗಿ, ಧಾರವಾಡ, ಬೆಳಗಾವಿ, ಬಾಗಲಕೋಟೆ, ವಿಜಯಪುರ) ಈ ಕೆಳಗಿನ ಬೆಳೆಗಳು ಹೆಚ್ಚು ಲಾಭದಾಯಕವಾಗಿವೆ:\n\n"
                    "1. **ಧಾನ್ಯ ಬೆಳೆಗಳು (Cereals)**:\n"
                    "   • **ಗೋಧಿ (Wheat)**: ನವೆಂಬರ್ ಬಿತ್ತನೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತ ಸಮಯ. ಶಿಫಾರಸು ತಳಿಗಳು: ಲೋಕವಾನ್, ಜಿಡಬ್ಲ್ಯು-322, ಡಿಡಬ್ಲ್ಯುಆರ್-162, ಡಿಡಬ್ಲ್ಯುಆರ್-2006. ತಂಪಾದ ಹವಾಮಾನದಲ್ಲಿ ಕವಲೊಡೆಯುವುದು ಅಧಿಕವಾಗಿರುತ್ತದೆ.\n"
                    "   • **ಹಿಂಗಾರು ಜೋಳ (Rabi Jowar)**: ಉತ್ತರ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಬರನಿರೋಧಕ ಆಹಾರ ಬೆಳೆ. ತಳಿಗಳು: ಎಂ 35-1 ('ಮಾಲ್ದಂಡಿ'), ಮುಗುತಿ, ಬಿಜೆವಿ-44, ಸಿಎಸ್‌ವಿ-29ಆರ್.\n\n"
                    "2. **ದ್ವಿದಳ ಧಾನ್ಯಗಳು (Pulses)**:\n"
                    "   • **ಕಡಲೆ / ಚಣಂಗಿ (Chickpea / Bengal Gram)**: ಬೀದರ್, ಕಲಬುರಗಿ, ಧಾರವಾಡ, ಗದಗ ಜಿಲ್ಲೆಗಳ ಪ್ರಮುಖ ಹಿಂಗಾರು ಬೆಳೆ. ತಳಿಗಳು: ಜೆಜಿ-11, ಅಣ್ಣಿಗೇರಿ-1, ಬಿಜೆಡಿ-103, ಜಾಕಿ-9218. ಮಣ್ಣಿನ ಆಳದ ತೇವಾಂಶವನ್ನು ಸಮರ್ಥವಾಗಿ ಬಳಸಿಕೊಂಡು ಉತ್ತಮ ಇಳುವರಿ ನೀಡುತ್ತದೆ.\n"
                    "   • **ಬಟಾಣಿ (Field Pea)**: ಕಡಿಮೆ ಅವಧಿಯಲ್ಲಿ ಹಸಿರು ಕಾಯಿ ಮತ್ತು ಒಣಕಾಳಿಗಾಗಿ ನವೆಂಬರ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಬಹುದು.\n\n"
                    "3. **ಎಣ್ಣೆಕಾಳು ಬೆಳೆಗಳು (Oilseeds)**:\n"
                    "   • **ಸೂರ್ಯಕಾಂತಿ (Sunflower)**: ನವೆಂಬರ್ ಅಂತ್ಯದವರೆಗೆ ಬಿತ್ತನೆ ಮಾಡಬಹುದು (ತಳಿಗಳು: ಕೆಬಿಎಸ್‌ಎಚ್-1, ಆರ್‌ಎಸ್‌ಎಫ್‌ಎಚ್-130).\n"
                    "   • **ಕುಸುಬೆ / ಕರಡಿ (Safflower)**: ಆಳವಾದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಬೇರು ಇಳಿಸಿ ಬೆಳೆಯುವ ಅತ್ಯುತ್ತಮ ಹಿಂಗಾರು ಎಣ್ಣೆಕಾಳು (ತಳಿಗಳು: ಎ-1, ಪಿಬಿಎನ್‌ಎಸ್-12).\n"
                    "   • **ಸಾಸಿವೆ (Mustard)**: ಕಡಿಮೆ ನೀರಿನಲ್ಲಿ 80-90 ದಿನಗಳಲ್ಲಿ ಬರುವ ಚಳಿಗಾಲದ ಬೆಳೆ.\n\n"
                    "4. **ತರಕಾರಿ ಮತ್ತು ಸಂಬಾರ ಬೆಳೆಗಳು**:\n"
                    "   • **ಈರುಳ್ಳಿ (ಹಿಂಗಾರು ಈರುಳ್ಳಿ), ಕ್ಯಾರೆಟ್, ಎಲೆಕೋಸು, ಹೂಕೋಸು, ಹಸಿಮೆಣಸಿನಕಾಯಿ ಮತ್ತು ಬೆಳ್ಳುಳ್ಳಿ** ನಾಟಿ ಮಾಡಲು ನವೆಂಬರ್ ಅತ್ಯುತ್ತಮ ಸಮಯ."
                )
            elif lang_code == "hi":
                return (
                    "🌾 **कर्नाटक में नवंबर (रबी / शीतकालीन मौसम) में बुवाई के लिए सर्वोत्तम प्रमुख फसलें**:\n\n"
                    "नवंबर में रबी शीतकालीन मौसम की शुरुआत के साथ (रात्रिकालीन तापमान 16–20°C ठंडा रहने और मिट्टी में अवशिष्ट नमी के कारण) कर्नाटक के उत्तरी व मध्य जिलों (बीदर, कलबुर्गी, धारवाड़, बेलगावी, विजयपुरा) में निम्नलिखित फसलें सबसे अधिक लाभकारी हैं:\n\n"
                    "1. **अनाज फसलें (Cereals)**:\n"
                    "   • **गेहूं (Wheat)**: नवंबर माह बुवाई के लिए सर्वोत्तम समय है। उन्नत किस्में: लोकवान, GW-322, DWR-162। ठंडे मौसम में कल्ले अधिक फूटते हैं।\n"
                    "   • **रबी ज्वार (Rabi Jowar)**: कर्नाटक की प्रमुख सूखा-सहनशील खाद्य फसल। किस्में: M 35-1 (मालदांडी), मुगुथी, CSV-29R।\n\n"
                    "2. **दलहन फसलें (Pulses)**:\n"
                    "   • **चना (Chickpea / Bengal Gram)**: बीदर, कलबुर्गी, धारवाड़ व गदग की प्रमुख रबी दाल। किस्में: JG-11, अन्नीगेरी-1, BGD-103, जाकी-9218। यह मिट्टी की अवशिष्ट नमी पर सर्वोत्तम पैदावार देती है।\n"
                    "   • **मटर (Field Pea)**: कम समय में तैयार होने वाली रबी दलहन।\n\n"
                    "3. **तिलहन फसलें (Oilseeds)**:\n"
                    "   • **सूरजमुखी (Sunflower)**: नवंबर बुवाई हेतु उत्तम (किस्में: KBSH-1, RSFH-130)।\n"
                    "   • **कुसुम / करड़ी (Safflower)**: गहरी काली मिट्टी में कम पानी में भरपूर पैदावार (किस्में: A-1, PBNS-12)।\n"
                    "   • **सरसों (Mustard)**: 85-90 दिन की शीतकालीन नकदी फसल।\n\n"
                    "4. **सब्जी एवं मसाला फसलें**:\n"
                    "   • **रबी प्याज, लहसुन, गाजर, पत्तागोभी, फूलगोभी व हरी मिर्च** की रोपाई हेतु नवंबर सर्वोत्तम समय है।"
                )
            else:
                return (
                    "🌾 **Best Crops for November / Rabi (Cool Season) Sowing in Karnataka**:\n\n"
                    "With the onset of the cool Rabi winter season in November (cool night temperatures of 16–20°C and conserved subsoil moisture in black and loamy soils), the following crops are most recommended across Karnataka agro-climatic zones (especially Bidar, Kalaburagi, Dharwad, Belagavi, and Vijayapura):\n\n"
                    "1. **Cereals**:\n"
                    "   • **Wheat**: Prime sowing window active throughout November. High-yielding varieties: Lokwan, GW-322, DWR-162, DWR-2006. Cool winter temperatures encourage vigorous tillering.\n"
                    "   • **Rabi Jowar (Sorghum)**: Flagship drought-resilient food crop for Northern Karnataka. Varieties: M 35-1 ('Maldandi'), Muguthi, CSV-29R.\n\n"
                    "2. **Pulses**:\n"
                    "   • **Chickpea / Bengal Gram (Chana)**: Top cool-season pulse for Bidar, Kalaburagi, and Dharwad. Varieties: JG-11, Annigeri-1, BGD-103, JAKI-9218. Efficiently utilizes conserved black soil moisture.\n"
                    "   • **Field Pea (Matar)**: Short-duration winter legume for green pods and dry grain.\n\n"
                    "3. **Oilseeds**:\n"
                    "   • **Sunflower**: Suitable for late Kharif / Rabi sowing up to late November (KBSH-1, RSFH-130).\n"
                    "   • **Safflower (Kusube)**: Exceptional taproot drought tolerance in deep vertisols (A-1, PBNS-12).\n"
                    "   • **Mustard (Rabi Sarson)**: Low water requirement winter cash crop (80-90 days).\n\n"
                    "4. **Vegetables & Commercial Horticulture**:\n"
                    "   • **Rabi Onion, Garlic, Carrot, Cabbage, Cauliflower, and Green Chillies**: Ideal transplanting window."
                )
        elif month in [6, 7, 8, 9]:
            # KHARIF (SOUTHWEST MONSOON)
            if lang_code == "kn":
                return (
                    "🌾 **ಕರ್ನಾಟಕದಲ್ಲಿ ಮುಂಗಾರು / ಖಾರಿಫ್ ಹಂಗಾಮಿನಲ್ಲಿ (ಜೂನ್–ಜುಲೈ) ಬಿತ್ತನೆಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು**:\n\n"
                    "ನೈಋತ್ಯ ಮುಂಗಾರು ಮಳೆಯ ಆರಂಭದೊಂದಿಗೆ ಕರ್ನಾಟಕದ ವಿವಿಧ ಜಿಲ್ಲೆಗಳಿಗೆ ಈ ಕೆಳಗಿನ ಬೆಳೆಗಳು ಹೆಚ್ಚು ಶಿಫಾರಸು ಮಾಡಲ್ಪಟ್ಟಿವೆ:\n\n"
                    "1. **ಧಾನ್ಯಗಳು**: ಭತ್ತ (ಕರಾವಳಿ ಹಾಗೂ ನೀರಾವರಿ ಪ್ರದೇಶ), ಮೆಕ್ಕೆಜೋಳ (ಬಯಲು ಸೀಮೆ), ರಾಗಿ (ದಕ್ಷಿಣ ಒಣಭೂಮಿ).\n"
                    "2. **ವಾಣಿಜ್ಯ ಮತ್ತು ಎಣ್ಣೆಕಾಳು**: ಹತ್ತಿ (ಉತ್ತರ ಕರ್ನಾಟಕ), ಶೇಂಗಾ (ಕೆಂಪು ಗೋಡು ಮಣ್ಣು), ಸೋಯಾಬೀನ್ (ಬೆಳಗಾವಿ, ಬೀದರ್, ಧಾರವಾಡ).\n"
                    "3. **ದ್ವಿದಳ ಧಾನ್ಯಗಳು**: ತೊಗರಿ (ಕಲಬುರಗಿ, ಬೀದರ್), ಹೆಸರು ಮತ್ತು ಉದ್ದು (ಅಲ್ಪಾವಧಿ ಬೆಳೆಗಳು)."
                )
            elif lang_code == "hi":
                return (
                    "🌾 **कर्नाटक में खरीफ मौसम (जून–जुलाई) में बुवाई के लिए सर्वोत्तम फसलें**:\n\n"
                    "दक्षिण-पश्चिम मानसून के साथ निम्नलिखित फसलें सबसे अधिक उपयुक्त हैं:\n\n"
                    "1. **अनाज**: धान (सिंचित व तटीय क्षेत्र), मक्का (दावणगेरे, हावेरी), रागी (दक्षिण शुष्क क्षेत्र)।\n"
                    "2. **नकदी व तिलहन**: कपास (काली मिट्टी), मूंगफली (लाल दोमट), सोयाबीन (बीदर, बेलगावी, धारवाड़)।\n"
                    "3. **दलहन**: अरहर/तुअर (कलबुर्गी, बीदर), मूंग व उड़द (अल्पकालिक फसलें)।"
                )
            else:
                return (
                    "🌾 **Best Crops for Kharif / Monsoon Sowing (June–July) in Karnataka**:\n\n"
                    "With the Southwest monsoon onset, recommended crops include:\n\n"
                    "1. **Cereals**: Paddy (Coastal & Canal Irrigated), Maize (Belagavi, Haveri plains), Ragi (Southern red soils).\n"
                    "2. **Cash & Oilseeds**: Cotton (Black vertisols), Groundnut (Sandy loam), Soybean (Belagavi, Bidar, Dharwad).\n"
                    "3. **Pulses**: Tur / Pigeon Pea (Kalaburagi, Bidar), Green Gram & Blackgram (catch crops)."
                )
        else:
            # SUMMER / ZAID (MARCH - MAY)
            if lang_code == "kn":
                return (
                    "🌾 **ಕರ್ನಾಟಕದಲ್ಲಿ ಬೇಸಿಗೆ (ಜಾಯದ್ ಹಂಗಾಮು) ಬಿತ್ತನೆಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು (ಮಾರ್ಚ್–ಮೇ)**:\n\n"
                    "ಬೇಸಿಗೆಯಲ್ಲಿ ನೀರಾವರಿ ಸೌಲಭ್ಯವಿರುವ ಪ್ರದೇಶಗಳಿಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು:\n\n"
                    "1. **ಬೇಸಿಗೆ ಶೇಂಗಾ / ಕಡಲೆಕಾಯಿ (TMV-2)**: ಬಿಸಿಲಿನಲ್ಲಿ ಉತ್ತಮ ಇಳುವರಿ.\n"
                    "2. **ಬೇಸಿಗೆ ಹೆಸರು ಮತ್ತು ಉದ್ದು**: 60-65 ದಿನಗಳಲ್ಲಿ ಕಟಾವಿಗೆ ಬರುವ ದ್ವಿದಳ ಧಾನ್ಯ.\n"
                    "3. **ಕಲ್ಲಂಗಡಿ ಮತ್ತು ಕರಬೂಜ**: ಬೇಸಿಗೆ ಮಾರುಕಟ್ಟೆಗೆ ಅತಿ ಹೆಚ್ಚು ಲಾಭದಾಯಕ ತೋಟಗಾರಿಕಾ ಬೆಳೆಗಳು.\n"
                    "4. **ಬೇಸಿಗೆ ಮೇವಿನ ಮೆಕ್ಕೆಜೋಳ ಹಾಗೂ ತರಕಾರಿಗಳು (ಬೆಂಡೆ, ಸೌತೆಕಾಯಿ)**."
                )
            elif lang_code == "hi":
                return (
                    "🌾 **कर्नाटक में जायद / ग्रीष्मकालीन (मार्च–मई) मौसम के लिए अनुशंसित फसलें**:\n\n"
                    "सिंचाई सुविधा उपलब्ध होने पर निम्नलिखित फसलें अत्यधिक लाभकारी हैं:\n\n"
                    "1. **ग्रीष्मकालीन मूंगफली (TMV-2)**: अधिक धूप में उत्तम तेल व पैदावार।\n"
                    "2. **ग्रीष्मकालीन मूंग व उड़द**: 60-65 दिन की अल्पकालिक दलहन।\n"
                    "3. **तरबूज व खरबूजा**: ग्रीष्मकालीन बाजार में सर्वाधिक मांग और मुनाफा।\n"
                    "4. **सब्जियां (भिंडी, खीरा, ककड़ी) एवं चारा मक्का**।"
                )
            else:
                return (
                    "🌾 **Best Crops for Summer / Zaid Season in Karnataka (March–May)**:\n\n"
                    "With assured borewell or canal irrigation, top options include:\n\n"
                    "1. **Summer Groundnut (TMV-2)**: High sunshine hours promote heavy pod development.\n"
                    "2. **Summer Green Gram (Moong)**: 60-65 day catch crop enriching soil nitrogen.\n"
                    "3. **Watermelon & Muskmelon**: High-demand commercial cucurbits.\n"
                    "4. **Horticultural Vegetables (Okra, Cucumber) & Fodder Maize**."
                )

    def generate_planner_agent_strategy(
        self,
        crop: str = "Rice",
        disease: Optional[str] = None,
        price: Optional[str] = None,
        district: Optional[str] = "Dharwad",
        irrigation_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        soil_type: Optional[str] = None,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Synthesizes all multi-agent modules (Crop Recommendation, Disease Detection,
        Market Price Agmarknet, Smart Irrigation, and Live District Weather) into a
        holistic, 360-degree AI Agronomist Strategic Action Plan dynamically tailored
        to the active calendar month, season, agro-climatic zone, and soil.
        """
        crop_clean = (crop or "Rice").strip()
        disease_clean = (disease or "None detected (Healthy)").strip()
        price_clean = (price or "Standard Market Rate").strip()
        district_clean = (district or "Karnataka").strip()
        lang_code = lang.lower() if lang in ["kn", "hi", "en"] else "en"

        irri_text = ""
        if irrigation_data:
            litres = irrigation_data.get("total_litres_day", "Standard")
            runtime = irrigation_data.get(f"runtime_{lang_code}", irrigation_data.get("runtime_en", ""))
            irri_text = f"Daily Water: {litres} L/day, Runtime: {runtime}"

        weather_text = ""
        if weather_data:
            t = weather_data.get("temp", "28")
            h = weather_data.get("humidity", "60")
            d = weather_data.get("desc", "Clear")
            weather_text = f"Temp: {t}°C, Humidity: {h}%, Weather: {d}"

        # Generate the fully localized dynamic blueprint fallback data for all 3 languages
        fallback_data = self._build_planner_fallback_strategy(
            crop_clean, disease_clean, price_clean, district_clean, irri_text, weather_text,
            weather_data=weather_data, soil_type=soil_type, lang=lang_code
        )

        now_dt = datetime.now()
        month_name = now_dt.strftime("%B")
        month_num = now_dt.month
        season_name = "Rabi (Winter / Cool Season)" if month_num in [10, 11, 12, 1, 2] else ("Kharif (Monsoon Season)" if month_num in [6, 7, 8, 9] else "Summer / Zaid Season")

        # Step 2: If live LLM is available, invoke Gemini with strictly grounded seasonal parameters
        if self.llm is not None and LANGCHAIN_AVAILABLE:
            try:
                prompt = (
                    f"You are the Lead AI Agronomist for SmartAgri orchestrating a comprehensive 360-degree Farm Management Plan.\n"
                    f"Synthesize the following live farm telemetry and AI predictions:\n"
                    f"• Current Calendar Date & Active Month: {now_dt.strftime('%B %Y')} (Month {month_num})\n"
                    f"• Active Agricultural Season: {season_name} (DO NOT assume June or Kharif; ground all advice in {month_name}!)\n"
                    f"• Location District: {district_clean}, Karnataka\n"
                    f"• Recommended / Target Crop: {crop_clean}\n"
                    f"• Plant Disease Diagnostic: {disease_clean}\n"
                    f"• Agmarknet Expected Market Price: {price_clean}\n"
                    f"• Live Weather Micro-Climate: {weather_text or 'Normal seasonal weather'}\n"
                    f"• Soil Characteristics: {soil_type or 'Deep Black / Loam Soil'}\n"
                    f"• Precision Irrigation Index: {irri_text or 'Standard schedule'}\n\n"
                    f"Provide a structured, step-by-step 360-degree Farm Decision Strategy covering:\n"
                    f"1. 🌾 **Executive Decision & Farm Readiness Assessment** (Overall viability for {crop_clean} in {district_clean} during {month_name})\n"
                    f"2. 🚨 **Plant Health & Disease Intervention** (Immediate organic & chemical spray protocol if disease present, or preventive IPM)\n"
                    f"3. 🌱 **Sowing, Spacing & Smart Irrigation Blueprint** (Sowing window for {month_name}, seed rate, and watering interval by growth stages)\n"
                    f"4. 🌿 **Nutrient Management (NPK Fertilizer Schedule)** (Exact split application: Basal, Tillering/Vegetative, Flowering)\n"
                    f"5. 💰 **Market Timing & Profit Realization** (Mandi price trend analysis, harvesting window, sell immediately vs warehouse storage)\n"
                    f"6. 🌾 **Top Recommended Crops for {month_name} ({season_name}) in {district_clean}** (Cereals, Pulses, Oilseeds)\n"
                    f"7. 🏛 **Applicable Karnataka Govt Subsidies** (e.g. Raitha Siri, PMFBY insurance, PMKSY Drip subsidy)\n\n"
                    f"Format with clear emojis, bullet points, and exact dosages (g/L or kg/ha). Be encouraging and practical.\n"
                    f"Language: Must be written completely in {lang_code.upper()} language."
                )
                res = self.ask_agronomist_rag(prompt, lang=lang_code)
                answer = res.get("answer", "")
                if answer and self._is_response_complete(answer) and "June" not in answer:
                    return {
                        "ai_plan": answer,
                        "ai_plan_en": answer if lang_code == "en" else fallback_data.get("ai_plan_en", ""),
                        "ai_plan_kn": answer if lang_code == "kn" else fallback_data.get("ai_plan_kn", ""),
                        "ai_plan_hi": answer if lang_code == "hi" else fallback_data.get("ai_plan_hi", ""),
                        "sources": res.get("sources", [f"[ICAR-KVK {district_clean} & UAS Seasonal Guidelines]"]),
                        "provider": res.get("provider", self.provider_name)
                    }
            except Exception as e:
                print(f"[Planner AI] Live LLM setup notice: {e}")

        return fallback_data

    def _build_planner_fallback_strategy(
        self,
        crop: str,
        disease: str,
        price: str,
        district: str,
        irri_text: str,
        weather_text: str,
        weather_data: Optional[Dict[str, Any]] = None,
        soil_type: Optional[str] = None,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Deterministic, fully dynamic, multi-agent synthesized 360° Agronomic Blueprint
        tailored to active month, season, weather micro-climate, soil, and district.
        Generates full versions in English, Kannada, and Hindi.
        """
        now = datetime.now()
        month = now.month
        year = now.year

        temp_val = 22.0
        humidity_val = 50.0
        weather_desc = "Clear sky"
        if weather_data:
            try:
                temp_val = float(weather_data.get('temp', 22.0))
                humidity_val = float(weather_data.get('humidity', 50.0))
                weather_desc = str(weather_data.get('desc', 'Clear sky'))
            except Exception:
                pass

        # Soil classification
        s_lower = (soil_type or '').lower()
        is_black_soil = any(k in s_lower for k in ['black', 'clay', 'vertisol']) or any(
            d in district.lower() for d in ['bidar', 'kalaburagi', 'dharwad', 'vijayapura', 'bagalkot', 'raichur', 'gadag', 'koppal', 'ballari', 'belagavi']
        )
        soil_en = "Deep Black Cotton Soil (High subsoil moisture retention)" if is_black_soil else "Loamy / Red Loam Soil (Well-drained)"
        soil_kn = "ಆಳವಾದ ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (ಹೆಚ್ಚು ತೇವಾಂಶ ಧಾರಣ ಶಕ್ತಿ)" if is_black_soil else "ಗೋಡು / ಕೆಂಪು ಮಣ್ಣು (ಉತ್ತಮ ನೀರು ಬಸಿದುಹೋಗುವಿಕೆ)"
        soil_hi = "गहरी काली कपास मिट्टी (उच्च नमी धारण क्षमता)" if is_black_soil else "दोमट / लाल दोमट मिट्टी (उत्तम जल निकास)"

        # Crop names localized
        import translations
        crop_en = translations.get_crop_name(crop, 'en')
        crop_kn = translations.get_crop_name(crop, 'kn')
        crop_hi = translations.get_crop_name(crop, 'hi')

        # District localized
        dist_tr = translations.DISTRICT_TRANSLATIONS.get(district, {})
        district_en = dist_tr.get('en', district)
        district_kn = dist_tr.get('kn', district).split(' (')[0].strip()
        district_hi = dist_tr.get('hi', district).split(' (')[0].strip()

        # Disease status
        has_disease = disease and "healthy" not in disease.lower() and "none" not in disease.lower() and "ಲಭ್ಯವಿಲ್ಲ" not in disease and "उपलब्ध" not in disease
        dis_en = (
            f"Active Pathogen Detected: **{disease}**. Immediately rogue out severely infected foliage. Apply prophylactic Neem Oil (3-5 ml/L) or targeted fungicide (Mancozeb 2.5 g/L / Hexaconazole 1 ml/L) during early morning or evening hours."
            if has_disease else
            "Plant health is optimal (No critical pathogen reported). Practice preventive seed treatment with Trichoderma viride (4 g/kg seed)."
        )
        dis_kn = (
            f"ರೋಗ ಪತ್ತೆಯಾಗಿದೆ: **{disease}**. ತಕ್ಷಣವೇ ರೋಗಗ್ರಸ್ತ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ. ಜೈವಿಕವಾಗಿ ಬೇವಿನ ಎಣ್ಣೆ (3-5 ಮಿ.ಲೀ/ಲೀ) ಅಥವಾ ಶಿಲೀಂಧ್ರನಾಶಕ ಮ್ಯಾಂಕೋಜೆಬ್ (2.5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ."
            if has_disease else
            "ಸಸ್ಯ ಆರೋಗ್ಯ ಉತ್ತಮವಾಗಿದೆ (ಯಾವುದೇ ಸಕ್ರಿಯ ರೋಗವಿಲ್ಲ). ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮ (4 ಗ್ರಾಂ/ಕೆಜಿ) ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಮಾಡಿ."
        )
        dis_hi = (
            f"रोग पहचाना गया: **{disease}**। तुरंत संक्रमित पत्तियों को तोड़कर नष्ट करें। नीम का तेल (3-5 मिली/लीटर) या मैंकोजेब (2.5 ग्राम/लीटर) का छिड़काव करें।"
            if has_disease else
            "फसल स्वास्थ्य अनुकूल है (कोई सक्रिय रोग दर्ज नहीं)। बुवाई से पूर्व ट्राइकोडर्मा (4 ग्राम/किग्रा) से बीजोपचार अवश्य करें।"
        )

        # -------------------------------------------------------------
        # BUILD ENGLISH BLUEPRINT
        # -------------------------------------------------------------
        if month in [10, 11, 12, 1, 2]:
            month_title_en = f"November / Rabi (Winter Season) Sowing in {district_en}, Karnataka"
            season_diag_en = (
                f"• **Active Season**: Rabi (Winter / Cool Season) — November Sowing & Early Crop Establishment.\n"
                f"• **Live Weather Micro-Climate**: {temp_val:.1f}°C, {humidity_val:.0f}% Humidity, {weather_desc}. "
                f"Cool night temperatures (~16–20°C in Northern Karnataka) create optimal growing conditions for cool-season C3 crops (Wheat, Chickpea), minimizing pest reproduction and slowing evaporative stress.\n"
                f"• **Soil & Moisture Management ({soil_en})**: Conserves post-monsoon subsoil moisture. Regulated micro-irrigation provides essential root-zone hydration without causing waterlogging or collar rot."
            )
            crops_season_en = (
                f"1. **Cereals**:\n"
                f"   • **Wheat (Lokwan, GW-322, DWR-162)**: Prime sowing window throughout November in Northern Karnataka.\n"
                f"   • **Rabi Jowar (M 35-1 'Maldandi', Muguthi, CSV-29R)**: Premier drought-resilient food crop for deep black soils.\n"
                f"2. **Pulses**:\n"
                f"   • **Chickpea / Bengal Gram (JG-11, Annigeri-1, BGD-103)**: Major cool-season nitrogen-fixing pulse for {district_en}.\n"
                f"3. **Oilseeds**:\n"
                f"   • **Sunflower (KBSH-1, RSFH-130)** & **Safflower / Kusube (A-1, PBNS-12)**: Deep taproot systems utilizing subsoil moisture."
            )
        else:
            month_title_en = f"Kharif / Monsoon Sowing in {district_en}, Karnataka"
            season_diag_en = (
                f"• **Active Season**: Kharif (Monsoon Season).\n"
                f"• **Live Weather**: {temp_val:.1f}°C, {humidity_val:.0f}% Humidity, {weather_desc}.\n"
                f"• **Soil**: {soil_en}."
            )
            crops_season_en = (
                "1. **Cereals**: Paddy, Maize, Ragi\n"
                "2. **Cash & Oilseeds**: Cotton, Groundnut, Soybean\n"
                "3. **Pulses**: Tur / Redgram, Green Gram, Blackgram"
            )

        plan_en = (
            f"🌾 **AI Agronomist Strategic Blueprint — {month_title_en}**:\n\n"
            f"📍 **1. Agro-Climatic & Live Weather Diagnostics ({district_en})**:\n"
            f"{season_diag_en}\n\n"
            f"🌱 **2. Target Crop Strategic Roadmap — {crop_en}**:\n"
            f"• **Sowing Window & Seed Rate**: Active Sowing Window. Use certified seed (40-45 kg/acre for Wheat, 25-30 kg/acre for Chickpea) treated with bio-fungicide.\n"
            f"• **Precision Irrigation**: {irri_text or 'Stage-based scheduling: Irrigate during tillering, flowering, and grain filling stages'}.\n"
            f"• **Balanced NPK Nutrition**: Apply 100% Phosphorus (DAP) + 50% Potash + 25% Nitrogen as Basal dose; top-dress remaining Nitrogen in 2 equal splits at tillering and flowering.\n"
            f"• **Market Mandi Realization**: Current expected rate: {price}. Where prices exceed Govt MSP, sell directly at APMC; utilize warehouse receipt storage if local arrivals cause temporary price dips.\n"
            f"• **Plant Health Status**: {dis_en}\n\n"
            f"🌾 **3. Recommended Crops for This Season in {district_en}**:\n"
            f"{crops_season_en}\n\n"
            f"🏛️ **4. Government Subsidies & Risk Protection**:\n"
            f"• Enroll in **PMFBY Crop Insurance** for seasonal weather risk coverage.\n"
            f"• Avail 75–90% drip/sprinkler subsidy under **PMKSY / Karnataka Raitha Siri Scheme**."
        )

        # -------------------------------------------------------------
        # BUILD KANNADA BLUEPRINT
        # -------------------------------------------------------------
        if month in [10, 11, 12, 1, 2]:
            month_title_kn = f"ನವೆಂಬರ್ / ಹಿಂಗಾರು (ರಬಿ ಹಂಗಾಮು) ಬಿತ್ತನೆ ಕಾರ್ಯತಂತ್ರ — {district_kn} ಜಿಲ್ಲೆ"
            season_diag_kn = (
                f"• **ಪ್ರಸ್ತುತ ಹಂಗಾಮು**: ಹಿಂಗಾರು (ರಬಿ / ಚಳಿಗಾಲದ ಹಂಗಾಮು) — ನವೆಂಬರ್ ಬಿತ್ತನೆ ಮತ್ತು ಸಸ್ಯ ಬೆಳವಣಿಗೆಯ ಪ್ರಮುಖ ಹಂತ.\n"
                f"• **ಲೈವ್ ಹವಾಮಾನ ಸೂಚ್ಯಂಕ**: {temp_val:.1f}°C ಉಷ್ಣಾಂಶ, ಶೇ. {humidity_val:.0f} ತೇವಾಂಶ, {weather_desc}. "
                f"({district_kn} ಹಾಗೂ ಉತ್ತರ ಕರ್ನಾಟಕದ ಭಾಗದಲ್ಲಿ ರಾತ್ರಿ ವೇಳೆ 16–20°C ತಂಪಾದ ಹವಾಮಾನವು ಹಿಂಗಾರು ಗೋಧಿ ಮತ್ತು ಕಡಲೆ ಬೆಳೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತವಾಗಿದ್ದು, ರೋಗಬಾಧೆ ತಗ್ಗಿಸಿ ಸಸ್ಯ ಬೆಳವಣಿಗೆಯನ್ನು ಉತ್ತೇಜಿಸುತ್ತದೆ).\n"
                f"• **ಮಣ್ಣು ಮತ್ತು ತೇವಾಂಶ ನಿರ್ವಹಣೆ ({soil_kn})**: ಆಳವಾದ ಕಪ್ಪು ಹಾಗೂ ಗೋಡು ಮಣ್ಣು ಹಿಂಗಾರಿನಲ್ಲಿ ಭೂಮಿಯ ತೇವಾಂಶವನ್ನು ಚೆನ್ನಾಗಿ ಉಳಿಸಿಕೊಳ್ಳುತ್ತದೆ. ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ಹಿತಮಿತವಾಗಿ ನೀರು ಹಾಯಿಸಿ ಬೇರು ಕೊಳೆ ರೋಗ ತಡೆಗಟ್ಟಿ."
            )
            crops_season_kn = (
                f"1. **ಧಾನ್ಯ ಬೆಳೆಗಳು (Cereals)**:\n"
                f"   • **ಗೋಧಿ (Wheat - ಲೋಕವಾನ್, ಜಿಡಬ್ಲ್ಯು-322, ಡಿಡಬ್ಲ್ಯುಆರ್-162)**: ನವೆಂಬರ್ ತಿಂಗಳ ಚಳಿ ಹವಾಮಾನಕ್ಕೆ ಬೀದರ್, ಧಾರವಾಡ, ಬೆಳಗಾವಿ ಭಾಗದಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಇಳುವರಿ.\n"
                f"   • **ಹಿಂಗಾರು ಜೋಳ (Rabi Jowar - ಎಂ 35-1 'ಮಾಲ್ದಂಡಿ', ಮುಗುತಿ, ಸಿಎಸ್‌ವಿ-29ಆರ್)**: ಉತ್ತರ ಕರ್ನಾಟಕದ ಕಪ್ಪು ಮಣ್ಣಿನ ಪ್ರಮುಖ ಬರನಿರೋಧಕ ಆಹಾರ ಬೆಳೆ.\n"
                f"2. **ದ್ವಿದಳ ಧಾನ್ಯಗಳು (Pulses)**:\n"
                f"   • **ಕಡಲೆ (Bengal Gram / Chickpea - ಜೆಜಿ-11, ಅಣ್ಣಿಗೇರಿ-1, ಬಿಜೆಡಿ-103)**: {district_kn} ಜಿಲ್ಲೆಯ ಪ್ರಮುಖ ಹಿಂಗಾರು ಬೆಳೆ.\n"
                f"3. **ಎಣ್ಣೆಕಾಳು ಬೆಳೆಗಳು (Oilseeds)**:\n"
                f"   • **ಸೂರ್ಯಕಾಂತಿ (Sunflower - ಕೆಬಿಎಸ್‌ಎಚ್-1, ಆರ್‌ಎಸ್‌ಎಫ್‌ಎಚ್-130)** ಮತ್ತು **ಕುಸುಬೆ (Safflower - ಎ-1, ಪಿಬಿಎನ್‌ಎಸ್-12)**: ಮಣ್ಣಿನ ಆಳದ ತೇವಾಂಶ ಬಳಸಿಕೊಂಡು ಉತ್ತಮ ಇಳುವರಿ ನೀಡುವ ವಾಣಿಜ್ಯ ಬೆಳೆಗಳು."
            )
        else:
            month_title_kn = f"ಮುಂಗಾರು / ಖಾರಿಫ್ ಹಂಗಾಮಿನ ಬಿತ್ತನೆ ಕಾರ್ಯತಂತ್ರ — {district_kn} ಜಿಲ್ಲೆ"
            season_diag_kn = (
                f"• **ಪ್ರಸ್ತುತ ಹಂಗಾಮು**: ಮುಂಗಾರು (ಖಾರಿಫ್ ಹಂಗಾಮು).\n"
                f"• **ಹವಾಮಾನ**: {temp_val:.1f}°C, {humidity_val:.0f}% ತೇವಾಂಶ.\n"
                f"• **ಮಣ್ಣು**: {soil_kn}."
            )
            crops_season_kn = (
                "1. **ಧಾನ್ಯಗಳು**: ಭತ್ತ, ಮೆಕ್ಕೆಜೋಳ, ರಾಗಿ\n"
                "2. **ವಾಣಿಜ್ಯ ಮತ್ತು ಎಣ್ಣೆಕಾಳು**: ಹತ್ತಿ, ಶೇಂಗಾ, ಸೋಯಾಬೀನ್\n"
                "3. **ದ್ವಿದಳ ಧಾನ್ಯಗಳು**: ತೊಗರಿ, ಹೆಸರು, ಉದ್ದು"
            )

        plan_kn = (
            f"🌾 **AI ಕೃಷಿ ತಜ್ಞರ ವೈಜ್ಞಾನಿಕ ಕಾರ್ಯತಂತ್ರ ನೀಲನಕ್ಷೆ — {month_title_kn}**:\n\n"
            f"📍 **1. ಕೃಷಿ ಹವಾಮಾನ ಮತ್ತು ನೈಜ ಹವಾಮಾನ ವಿಶ್ಲೇಷಣೆ ({district_kn})**:\n"
            f"{season_diag_kn}\n\n"
            f"🌱 **2. ಮುಖ್ಯ ಶಿಫಾರಸು ಬೆಳೆಯ ಕಾರ್ಯತಂತ್ರ — {crop_kn}**:\n"
            f"• **ಬಿತ್ತನೆ ಕಾಲಾವಧಿ ಮತ್ತು ಬೀಜೋಪಚಾರ**: ಹಿಂಗಾರು ಬಿತ್ತನೆ ಸಮಯ ಸಕ್ರಿಯವಾಗಿದೆ (ನವೆಂಬರ್ 30 ರವರೆಗೆ). ಉತ್ತಮ ಮೊಳಕೆ ಸಾಮರ್ಥ್ಯವಿರುವ ಪ್ರಮಾಣಿತ ಬೀಜ ಬಳಸಿ, ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮ (4 ಗ್ರಾಂ/ಕೆಜಿ) ಜೈವಿಕ ಬೀಜೋಪಚಾರ ಮಾಡಿ.\n"
            f"• **ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ**: {irri_text or 'ಹಂತ-ಆಧರಿತ ನೀರಾವರಿ: ಕವಲೊಡೆಯುವಾಗ, ಹೂವಾಡುವಾಗ ಮತ್ತು ಕಾಳು ಕಟ್ಟುವ ಹಂತಗಳಲ್ಲಿ ಅಗತ್ಯ ನೀರು ಒದಗಿಸಿ'}.\n"
            f"• **ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ (NPK) ನಿರ್ವಹಣೆ**: ಬಿತ್ತನೆ ವೇಳೆ ಶೇ. 100 ರಂಜಕ (DAP), ಶೇ. 50 ಪೊಟ್ಯಾಶ್ ಹಾಗೂ ಶೇ. 25 ಸಾರಜನಕವನ್ನು ಅಡಿಗೊಬ್ಬರವಾಗಿ ನೀಡಿ; ಉಳಿದ ಸಾರಜನಕವನ್ನು 2 ಕಂತುಗಳಲ್ಲಿ ಮೇಲುಗೊಬ್ಬರವಾಗಿ ಹಾಕಿ.\n"
            f"• **ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಎಂಎಸ್‌ಪಿ ಲಾಭ**: ನಿರೀಕ್ಷಿತ ಎಪಿಎಂಸಿ ಮಂಡಿ ದರ {price}. ಬೆಲೆ ಉತ್ತಮವಾಗಿದ್ದಲ್ಲಿ ಮಂಡಿಯಲ್ಲಿ ಮಾರಾಟ ಮಾಡಿ; ಬೆಲೆ ಕಡಿಮೆಯಿದ್ದಲ್ಲಿ ಗೋದಾಮಿನಲ್ಲಿ ದಾಸ್ತಾನು ಮಾಡಿ ಗರಿಷ್ಠ ಬೆಲೆಗೆ ಮಾರಾಟ ಮಾಡಿ.\n"
            f"• **ಸಸ್ಯ ಸಂರಕ್ಷಣೆ ಮತ್ತು ಆರೋಗ್ಯ**: {dis_kn}\n\n"
            f"🌾 **3. {district_kn} ಜಿಲ್ಲೆಯಲ್ಲಿ ಈ ಹಂಗಾಮಿಗೆ ಸೂಕ್ತವಾದ ಪ್ರಮುಖ ಬೆಳೆಗಳು**:\n"
            f"{crops_season_kn}\n\n"
            f"🏛️ **4. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಬೆಳೆ ವಿಮೆ**:\n"
            f"• ಹವಾಮಾನ ವೈಪರೀತ್ಯದ ನಷ್ಟ ಪರಿಹಾರಕ್ಕೆ **PMFBY ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ** ನೋಂದಾಯಿಸಿ.\n"
            f"• **PMKSY ಹನಿ ನೀರಾವರಿ ಯೋಜನೆ** ಅಡಿಯಲ್ಲಿ ಶೇ. 90 ರವರೆಗೆ ಸಹಾಯಧನ ಪಡೆದು ನೀರು ಉಳಿಸಿ."
        )

        # -------------------------------------------------------------
        # BUILD HINDI BLUEPRINT
        # -------------------------------------------------------------
        if month in [10, 11, 12, 1, 2]:
            month_title_hi = f"नवंबर / रबी (शीतकालीन मौसम) बुवाई कार्ययोजना — {district_hi} जिला"
            season_diag_hi = (
                f"• **सक्रिय मौसम**: रबी (शीतकालीन) — नवंबर बुवाई एवं फसल स्थापना का प्रमुख चरण।\n"
                f"• **मौसम सूचकांक**: {temp_val:.1f}°C तापमान, {humidity_val:.0f}% आर्द्रता, {weather_desc}। "
                f"({district_hi} तथा उत्तर कर्नाटक में रात्रिकालीन ठंडा तापमान (16–20°C) रबी गेहूं एवं चना की वृद्धि के लिए अत्यंत अनुकूल है, जिससे कीट-व्याधियों का प्रकोप कम होता है)।\n"
                f"• **मिट्टी एवं नमी प्रबंधन ({soil_hi})**: गहरी काली व दोमट मिट्टी रबी के दौरान नमी संजोकर रखती है। सूक्ष्म सिंचाई (ड्रिप) द्वारा संतुलित पानी दें ताकि जलभराव या जड़ गलन न हो।"
            )
            crops_season_hi = (
                f"1. **अनाज फसलें (Cereals)**:\n"
                f"   • **गेहूं (Wheat - लोकवान, GW-322, DWR-162)**: उत्तरी कर्नाटक में नवंबर के ठंडे मौसम में बुवाई के लिए सर्वोत्तम।\n"
                f"   • **रबी ज्वार (Jowar - M 35-1 मालदांडी, मुगुथी)**: गहरी काली मिट्टी हेतु सर्वोत्तम सूखा-रोधी खाद्य फसल।\n"
                f"2. **दलहन फसलें (Pulses)**:\n"
                f"   • **चना (Chickpea / Bengal Gram - जेजी-11, अन्नीगेरी-1, बीजीडी-103)**: {district_hi} में रबी की प्रमुख नकदी दाल।\n"
                f"3. **तिलहन फसलें (Oilseeds)**:\n"
                f"   • **सूरजमुखी (Sunflower - KBSH-1)** एवं **कुसुम / करड़ी (Safflower - A-1)**: अवशिष्ट मिट्टी नमी पर भरपूर पैदावार देने वाली फसलें।"
            )
        else:
            month_title_hi = f"खरीफ / मानसून मौसम बुवाई कार्ययोजना — {district_hi} जिला"
            season_diag_hi = (
                f"• **सक्रिय मौसम**: खरीफ (मानसून मौसम)।\n"
                f"• **मौसम**: {temp_val:.1f}°C, {humidity_val:.0f}% आर्द्रता।\n"
                f"• **मिट्टी**: {soil_hi}।"
            )
            crops_season_hi = (
                "1. **अनाज**: धान, मक्का, रागी\n"
                "2. **नकदी व तिलहन**: कपास, मूंगफली, सोयाबीन\n"
                "3. **दलहन**: अरहर, मूंग, उड़द"
            )

        plan_hi = (
            f"🌾 **AI कृषि वैज्ञानिक रणनीतिक ब्लूप्रिंट — {month_title_hi}**:\n\n"
            f"📍 **1. कृषि-जलवायु एवं मौसम विश्लेषण ({district_hi})**:\n"
            f"{season_diag_hi}\n\n"
            f"🌱 **2. मुख्य अनुशंसित फसल कार्ययोजना — {crop_hi}**:\n"
            f"• **बुवाई की समय-सीमा एवं बीजोपचार**: रबी बुवाई का सक्रिय समय (30 नवंबर तक)। प्रमाणित बीजों का उपयोग करें और बुवाई पूर्व ट्राइकोडर्मा (4 ग्राम/किग्रा) से बीजोपचार करें।\n"
            f"• **सटीक सिंचाई समय-सारणी**: {irri_text or 'अवस्था-आधारित सिंचाई: कल्ले फूटते समय, फूल आने पर एवं दाना भराव अवस्था में समय पर सिंचाई करें'}.\n"
            f"• **संतुलित पोषक तत्व (NPK) प्रबंधन**: बुवाई के समय 100% फास्फोरस (DAP), 50% पोटाश और 25% नाइट्रोजन बेसल डोज के रूप में दें; शेष नाइट्रोजन को 2 खुराकों में टॉप ड्रेसिंग करें।\n"
            f"• **मंडी भाव एवं न्यूनतम समर्थन मूल्य (MSP) लाभ**: अनुमानित मंडी भाव {price} है। भाव अनुकूल होने पर एपीएमसी मंडी में विक्रय करें; भाव कम होने पर वेयरहाउस रसीद पर भंडारण कर बाद में लाभ कमाएं।\n"
            f"• **पौध संरक्षण एवं स्वास्थ्य**: {dis_hi}\n\n"
            f"🌾 **3. {district_hi} जिले में इस मौसम की प्रमुख अनुशंसित फसलें**:\n"
            f"{crops_season_hi}\n\n"
            f"🏛️ **4. सरकारी योजनाएं एवं वित्तीय सुरक्षा**:\n"
            f"• प्राकृतिक जोखिम से सुरक्षा हेतु **PMFBY प्रधानमंत्री फसल बीमा योजना** में अनिवार्य रूप से पंजीकरण कराएं।\n"
            f"• **PMKSY ड्रिप सिंचाई योजना** के तहत 80-90% तक सरकारी अनुदान प्राप्त करें।"
        )

        chosen_plan = plan_kn if lang == "kn" else (plan_hi if lang == "hi" else plan_en)
        return {
            "ai_plan": chosen_plan,
            "ai_plan_en": plan_en,
            "ai_plan_kn": plan_kn,
            "ai_plan_hi": plan_hi,
            "sources": [
                f"[ICAR-KVK {district_en} & UAS Seasonal Advisory]",
                "[Karnataka State Dept of Agriculture - Package of Practices]",
                f"[Live Mandi & Weather Telemetry - {district_en}]"
            ],
            "provider": "SmartAgri Multilingual Agronomist Engine"
        }


# Global singleton instance
agri_llm = AgriLlmService.get_instance()


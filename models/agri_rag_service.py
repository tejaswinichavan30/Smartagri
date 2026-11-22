"""
SmartAgri RAG (Retrieval-Augmented Generation) Service
Loads agricultural knowledge documents, manages embeddings and vector search index,
and provides context retrieval for the LangChain agent.
"""

import os
import glob
from typing import List, Dict, Any, Tuple

# Fallback vector index with TF-IDF / Cosine Similarity for robust offline / free usage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Datasets", "agri_knowledge")

class AgriDocument:
    def __init__(self, content: str, source: str, title: str = ""):
        self.page_content = content
        self.metadata = {"source": source, "title": title}

class AgriRagService:
    _instance = None

    def __init__(self):
        self.documents: List[AgriDocument] = []
        self.chunks: List[AgriDocument] = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.langchain_vectorstore = None
        self.is_initialized = False
        self.initialize_knowledge_base()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _split_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Simple, robust recursive-like paragraph and sentence splitter."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
            if len(current_chunk) + len(p_clean) < chunk_size:
                current_chunk = (current_chunk + "\n\n" + p_clean).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = p_clean

        if current_chunk:
            chunks.append(current_chunk)

        # Fallback if any single chunk is very large
        final_chunks = []
        for c in chunks:
            if len(c) > chunk_size * 1.5:
                sub_parts = c.split("\n- ")
                for sp in sub_parts:
                    if sp.strip():
                        final_chunks.append(sp.strip())
            else:
                final_chunks.append(c)

        return final_chunks

    def initialize_knowledge_base(self):
        """Loads all knowledge docs from Datasets/agri_knowledge and builds index."""
        if not os.path.exists(KNOWLEDGE_DIR):
            os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

        md_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))
        all_chunks = []

        for fpath in md_files:
            fname = os.path.basename(fpath)
            title = fname.replace("_", " ").replace(".md", "").title()
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                raw_chunks = self._split_text(text, chunk_size=500, overlap=80)
                for chunk in raw_chunks:
                    if len(chunk.strip()) > 30:
                        all_chunks.append(AgriDocument(content=chunk.strip(), source=fname, title=title))
            except Exception as e:
                print(f"[RAG Service] Error reading {fpath}: {e}")

        self.chunks = all_chunks

        # Build TF-IDF Vector Index for instant retrieval
        if self.chunks:
            corpus = [doc.page_content for doc in self.chunks]
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=3000, ngram_range=(1, 2))
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            self.is_initialized = True
            print(f"[RAG Service] Initialized successfully with {len(self.chunks)} knowledge chunks from {len(md_files)} documents.")
        else:
            print("[RAG Service] Warning: No knowledge chunks found.")

    def _expand_multilingual_query(self, query: str) -> str:
        """Expands Kannada/Hindi agricultural words into English search terms for TF-IDF retrieval."""
        q_clean = query.lower()
        expanded_terms = [query]

        # Multilingual Agriculture Keyword Mapping
        term_map = {
            # Months & Seasons
            "ಜೂನ್": "June Kharif monsoon sowing",
            "ಜುಲೈ": "July Kharif transplanting",
            "ಆಗಸ್ಟ್": "August Kharif mid season",
            "ಸೆಪ್ಟೆಂಬರ್": "September harvesting",
            "ಅಕ್ಟೋಬರ್": "October Rabi winter sowing",
            "ನವೆಂಬರ್": "November Rabi sowing",
            "ಡಿಸೆಂಬರ್": "December cold season",
            "ಜನವರಿ": "January harvesting",
            "ಫೆಬ್ರವರಿ": "February Summer Zaid sowing",
            "ಮಾರ್ಚ್": "March Summer season",
            "ಮುಂಗಾರು": "Kharif southwest monsoon June July",
            "ಹಿಂಗಾರು": "Rabi northeast winter October November",
            "ಬೇಸಿಗೆ": "Summer Zaid February March irrigation",
            "जून": "June Kharif monsoon sowing",
            "जुलाई": "July Kharif",
            "अक्टूबर": "October Rabi",
            "खरीफ": "Kharif monsoon June July",
            "रबी": "Rabi winter October November",

            # Actions & Concepts
            "ಕರ್ನಾಟಕ": "Karnataka state agriculture",
            "ಕರ್ನಾಟಕದಲ್ಲಿ": "Karnataka districts soil weather",
            "ಬಿತ್ತನೆ": "sowing planting cultivation season",
            "ಬಿತ್ತನೆ ಮಾಡಲು": "sowing planting crops varieties",
            "ಸೂಕ್ತವಾದ": "suitable recommended best",
            "ಬೆಳೆಗಳು": "crops varieties cultivation",
            "ಬೆಳೆ": "crop farming guide",
            "ಯಾವುವು": "which list varieties",
            "ಬುನ್ನಾಯಿ": "sowing planting",
            "बुवाई": "sowing planting varieties",
            "फसलें": "crops varieties cultivation",

            # Specific Crops
            "ಭತ್ತ": "paddy rice varieties Jyothi Jaya IR64",
            "ಅಕ್ಕಿ": "paddy rice",
            "ಮೆಕ್ಕೆಜೋಳ": "maize corn Deccan CP818",
            "ರಾಗಿ": "ragi finger millet GPU28 MR1",
            "ಹತ್ತಿ": "cotton Bunny Bt Vertisols",
            "ತೊಗರಿ": "redgram tur pigeonpea Kalaburagi GRG811",
            "ಶೇಂಗಾ": "groundnut peanut TMV2",
            "ನೆಲಗಡಲೆ": "groundnut peanut TMV2",
            "ಕಬ್ಬು": "sugarcane Co86032",
            "ಸೋಯಾಬೀನ್": "soybean JS335",
            "ಹೆಸರು": "greengram mungbean",
            "ಉದ್ದು": "blackgram urad",
            "ಕಡಲೆ": "chickpea bengal gram JG11",
            "ಗೋಧಿ": "wheat DWR162",
            "ಟೊಮೆಟೊ": "tomato Arka Rakshak",
            "ಈರುಳ್ಳಿ": "onion Arka Kalyan",
            "ಮೆಣಸಿನಕಾಯಿ": "chilli Byadgi Sitara",
            "ಅಡಿಕೆ": "arecanut plantation",
            "ತೆಂಗು": "coconut plantation",

            # Irrigation & Water Management
            "ನೀರು": "irrigation water requirement depth schedule",
            "ನೀರಾವರಿ": "irrigation water interval schedule drip",
            "ಅವಧಿ": "interval schedule timing days",
            "ದಿನಗಳಿಗೊಮ್ಮೆ": "interval days frequency watering",
            "ಹನಿ ನೀರಾವರಿ": "drip irrigation efficiency",
            "ಸಿಂಚಾಯಿ": "irrigation watering interval schedule",
            "सिंचाई": "irrigation watering interval schedule stages",
            "पानी": "irrigation water requirement schedule",
            "पानी देना": "irrigation watering interval days",
            "अंतराल": "interval schedule days frequency",
            "मक्का": "maize corn irrigation schedule tasseling silking knee high",
            "मक्के": "maize corn irrigation schedule tasseling silking knee high",

            # Pests, Insects & Fall Armyworm
            "ಸೈನಿಕ ಹುಳು": "maize fall armyworm spodoptera frugiperda emamectin benzoate chlorantraniliprole whorl spray pest control",
            "ಸೈನಿಕ ಹುಳ": "maize fall armyworm spodoptera frugiperda emamectin benzoate chlorantraniliprole whorl spray pest control",
            "ಸೈನಿಕ": "maize fall armyworm pest spray",
            "ಹುಳು": "pest insect caterpillar borer worm larvae spray control",
            "ಹುಳ": "pest insect caterpillar borer worm larvae spray control",
            "ಪರಿಹಾರ": "remedy control measure treatment management spray",
            "ನಿಯಂತ್ರಣ": "control prevention management pesticide spray",
            "ಆರ್ಮಿವರ್ಮ್": "fall armyworm spodoptera maize whorl spray",
            "armyworm": "maize fall armyworm spodoptera emamectin coragen whorl spray",
            "fall armyworm": "maize fall armyworm spodoptera chlorantraniliprole whorl",
            "फॉल आर्मीवर्म": "maize fall armyworm spodoptera chlorantraniliprole emamectin",
            "आर्मीवर्म": "maize fall armyworm pest control",
            "सैनिक कीट": "maize fall armyworm spodoptera pest",
            "इल्ली": "caterpillar borer pest larvae spray",
            "सुंडी": "caterpillar borer pest spray",
            "रोकथाम": "prevention control remedy spray",
            "उपचार": "treatment remedy fungicide pesticide",

            # Agronomic Needs
            "ಗೊಬ್ಬರ": "fertilizer NPK nitrogen phosphorus potassium urea DAP",
            "ಯೂರಿಯಾ": "urea nitrogen fertilizer",
            "ಡಿಎಪಿ": "DAP phosphorus fertilizer",
            "ಖಾದ": "fertilizer manure compost",
            "ರೋಗ": "disease fungal blight blast rust spray",
            "ಕೀಟ": "pest insect borer armyworm control",
            "ಕೀಟನಾಶಕ": "insecticide pesticide spray dosage",
            "ಯೋಜನೆ": "government scheme PM-KISAN subsidy",
            "ಸಬ್ಸಿಡಿ": "subsidy scheme financial assistance",
            "ರೈತ ಸಿರಿ": "Raitha Siri millet subsidy",
            "ಗಂಗಾ ಕಲ್ಯಾಣ": "Ganga Kalyana irrigation borewell scheme",
            "ಖಾದ್": "fertilizer NPK",
            "रोग": "disease pest blight spray",
            "कीट": "pest insect control",
            "दवा": "medicine pesticide fungicide spray",
            "योजना": "government scheme subsidy"
        }

        for k, v in term_map.items():
            if k in q_clean:
                expanded_terms.append(v)

        return " ".join(expanded_terms)

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.06) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant agricultural snippets for a query using tuned cosine similarity.
        Returns a list of dicts with content, snippet, source, title, and relevance score.
        """
        if not self.is_initialized or not self.chunks or self.tfidf_vectorizer is None:
            return []

        try:
            expanded_query = self._expand_multilingual_query(query)
            query_vec = self.tfidf_vectorizer.transform([expanded_query])
            sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            top_indices = sims.argsort()[::-1][:top_k]
            results = []
            
            for idx in top_indices:
                score = float(sims[idx])
                if score >= min_score:  # Tuned empirical threshold based on domain evaluation
                    doc = self.chunks[idx]
                    snippet = doc.page_content.strip()
                    if len(snippet) > 280:
                        snippet = snippet[:280].rsplit(' ', 1)[0] + "..."
                    results.append({
                        "content": doc.page_content,
                        "snippet": snippet,
                        "source": doc.metadata.get("source", "ICAR/UAS Package of Practices"),
                        "title": doc.metadata.get("title", "Agriculture Advisory"),
                        "score": round(score, 4)
                    })
            
            return results
        except Exception as e:
            print(f"[RAG Service] Retrieval error: {e}")
            return []

    def get_rag_context_str(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
        """Formats retrieved snippets into context string and returns structured citations."""
        retrieved = self.retrieve(query, top_k=top_k)
        if not retrieved:
            return "No specific guidance found in verified local knowledge base. Consult your local KVK / Raitha Samparka Kendra for field-specific recommendations.", []

        context_lines = []
        sources = []
        for i, item in enumerate(retrieved, start=1):
            source_tag = f"[{item['title']}]"
            context_lines.append(f"Document {i} ({source_tag}):\n{item['content']}")
            sources.append({
                "title": item['title'],
                "source": item['source'],
                "snippet": item['snippet'],
                "score": item['score']
            })

        return "\n\n".join(context_lines), sources


# Global singleton
agri_rag = AgriRagService.get_instance()

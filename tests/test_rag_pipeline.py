"""
Test script for SmartAgri RAG pipeline and LLM service.
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.agri_rag_service import agri_rag
from models.agri_llm_service import agri_llm

def test_rag_service():
    print("\n--- 1. Testing RAG Knowledge Base Initialization ---")
    print(f"Total chunks indexed: {len(agri_rag.chunks)}")
    assert len(agri_rag.chunks) > 0, "No knowledge chunks were indexed!"
    print("✓ Knowledge chunks initialized successfully.")

    print("\n--- 2. Testing RAG Context Retrieval ---")
    test_queries = [
        "What is the fertilizer NPK requirement for rice?",
        "How to treat tomato early blight disease?",
        "What are the benefits of PM-KISAN scheme?",
        "Subsidies on drip irrigation"
    ]

    for q in test_queries:
        context, sources = agri_rag.get_rag_context_str(q, top_k=2)
        print(f"\nQuery: '{q}'")
        print(f"Sources retrieved: {sources}")
        print(f"Context snippet (first 150 chars): {context[:150]}...")
        assert len(sources) > 0, f"No sources retrieved for query: {q}"
    
    print("\n✓ RAG Context retrieval passed.")

def test_llm_service():
    print("\n--- 3. Testing Agri LLM Service Response ---")
    print(f"Active Provider: {agri_llm.provider_name}")
    
    res_en = agri_llm.ask_agronomist_rag("What fertilizer should I apply for Rice in Kharif?", lang="en")
    print(f"\nEnglish Response:\n{res_en.get('answer')[:300]}...")
    print(f"Sources: {res_en.get('sources')}")
    assert len(res_en.get("answer", "")) > 20, "Response is too short!"

    res_hi = agri_llm.ask_agronomist_rag("टमाटर में झुलसा रोग का क्या इलाज है?", lang="hi")
    print(f"\nHindi Response Preview:\n{res_hi.get('answer')[:200]}...")

    print("\n--- 4. Testing ML Explainability Synthesis ---")
    crop_exp = agri_llm.explain_crop_recommendation(
        crop="Rice", n=100, p=50, k=50, temp=28, humidity=80, ph=6.2, rainfall=200, lang="en"
    )
    print(f"Crop Recommendation Explanation Preview:\n{crop_exp[:250]}...")

    print("\n✓ All RAG & LLM tests completed successfully!")

if __name__ == "__main__":
    test_rag_service()
    test_llm_service()

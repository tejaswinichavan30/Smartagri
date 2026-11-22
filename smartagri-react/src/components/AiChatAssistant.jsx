import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext.jsx';
import { api } from '../api.js';

const QUICK_SUGGESTIONS = [
  { en: "🌿 Best fertilizer schedule for Rice?", hi: "🌿 धान के लिए सही खाद और उर्वरक?", kn: "🌿 ಭತ್ತದ ಬೆಳೆಗೆ ಸೂಕ್ತ ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ?" },
  { en: "🩺 How to cure Tomato Leaf Blight?", hi: "🩺 टमाटर के झुलसा रोग का जैविक व रासायनिक इलाज?", kn: "🩺 ಟೊಮೇಟೊ ಎಲೆ ಕರಕಲು ರೋಗ ನಿವಾರಣೆ ಹೇಗೆ?" },
  { en: "🏛 How to apply for PM-KISAN subsidy?", hi: "🏛 पीएम-किसान योजना के लिए कैसे आवेदन करें?", kn: "🏛 ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯ ಪ್ರಯೋಜನ ಹೇಗೆ ಪಡೆಯುವುದು?" },
  { en: "💧 Micro-irrigation subsidy guidelines?", hi: "💧 ड्रिप सिंचाई सब्सिडी के क्या नियम हैं?", kn: "💧 ಹನಿ ನೀರಾವರಿ ಸಬ್ಸಿಡಿ ಪಡೆಯುವ ವಿಧಾನ?" }
];

export default function AiChatAssistant({ dashboardContext = {} }) {
  const { lang, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend = input) => {
    const query = textToSend.trim();
    if (!query || loading) return;

    const userMsg = { id: Date.now(), role: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = messages
        .filter(m => m.id !== 'welcome')
        .map(m => ({ role: m.role, content: m.text }));

      const res = await api.chat(query, history, lang, dashboardContext);
      
      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: res.reply || res.answer || "I am analyzing the agricultural data for your question.",
        sources: res.sources || [],
        provider: res.provider || "SmartAgri RAG",
        hasRag: res.has_rag
      };

      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          text: "I could not connect to the Agronomist engine right now. Please verify your backend server.",
          sources: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = lang === 'hi' ? 'hi-IN' : lang === 'kn' ? 'kn-IN' : 'en-IN';
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      handleSend(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const clearChat = () => {
    setMessages([]);
  };

  // Build active dashboard summary badges
  const hasCrop = Boolean(dashboardContext?.crop?.name || dashboardContext?.crop?.crop);
  const hasPrice = Boolean(dashboardContext?.price?.price || dashboardContext?.price?.predictedPrice || dashboardContext?.price?.priceText);
  const hasDisease = Boolean(dashboardContext?.disease?.disease || dashboardContext?.disease?.predictedDisease);
  const hasIrrigation = Boolean(dashboardContext?.irrigation?.advice || dashboardContext?.irrigation?.crop);
  const hasPlanner = Boolean(dashboardContext?.planner?.summary || dashboardContext?.planner?.ai_plan);
  const hasAnyAgentResult = hasCrop || hasPrice || hasDisease || hasIrrigation || hasPlanner;

  // Build dynamic explanation questions
  const dynamicSuggestions = [
    ...(hasAnyAgentResult ? [{
      en: "📋 Explain all my dashboard results in simple words",
      hi: "📋 मेरे सभी डैशबोर्ड परिणामों को सरल भाषा में समझाएं",
      kn: "📋 ನನ್ನ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಫಲಿತಾಂಶಗಳನ್ನು ಸರಳವಾಗಿ ವಿವರಿಸಿ"
    }] : []),
    ...(hasCrop ? [{
      en: `🌱 Explain why ${dashboardContext?.crop?.name || dashboardContext?.crop?.crop || 'this crop'} was recommended for my soil`,
      hi: `🌱 समझाएं कि यह फसल मेरी मिट्टी के लिए क्यों सुझाई गई है`,
      kn: `🌱 ನನ್ನ ಮಣ್ಣಿಗೆ ಈ ಬೆಳೆ ಏಕೆ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ ಎಂದು ವಿವರಿಸಿ`
    }] : []),
    ...(hasDisease ? [{
      en: "🩺 Explain this plant disease and step-by-step treatment",
      hi: "🩺 इस पौधे के रोग का आसान भाषा में इलाज समझाएं",
      kn: "🩺 ಈ ಬೆಳೆ ರೋಗ ಮತ್ತು ಅದರ ಪರಿಹಾರ ಕ್ರಮಗಳನ್ನು ವಿವರಿಸಿ"
    }] : []),
    ...(hasPrice ? [{
      en: "💰 Explain the market price forecast and best selling time",
      hi: "💰 मंडी भाव पूर्वानुमान और फसल बेचने का सही समय बताएं",
      kn: "💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಮಾರಾಟದ ಉತ್ತಮ ಸಮಯ ತಿಳಿಸಿ"
    }] : []),
    ...(hasIrrigation ? [{
      en: "💧 Explain my precision irrigation schedule in simple terms",
      hi: "💧 मेरी फसल के लिए सिंचाई का सही समय और पानी की मात्रा बताएं",
      kn: "💧 ನನ್ನ ಬೆಳೆಗೆ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ಪ್ರಮಾಣವನ್ನು ಸರಳವಾಗಿ ವಿವರಿಸಿ"
    }] : []),
    ...(hasPlanner ? [{
      en: "🤖 Explain my complete farm plan step-by-step",
      hi: "🤖 मेरी संपूर्ण कृषि योजना को चरणबद्ध तरीके से समझाएं",
      kn: "🤖 ನನ್ನ ಸಂಪೂರ್ಣ ಕೃಷಿ ಯೋಜನೆಯನ್ನು ಹಂತ-ಹಂತವಾಗಿ ವಿವರಿಸಿ"
    }] : []),
    { en: "🌿 Best fertilizer schedule for Rice?", hi: "🌿 धान के लिए सही खाद और उर्वरक?", kn: "🌿 ಭತ್ತದ ಬೆಳೆಗೆ ಸೂಕ್ತ ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ?" },
    { en: "🏛 How to apply for PM-KISAN subsidy?", hi: "🏛 पीएम-किसान योजना के लिए कैसे आवेदन करें?", kn: "🏛 ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯ ಪ್ರಯೋಜನ ಹೇಗೆ ಪಡೆಯುವುದು?" }
  ];

  const renderFormattedText = (text) => {
    return text.split('\n').map((line, idx) => {
      if (line.startsWith('### ') || line.startsWith('## ') || line.startsWith('# ')) {
        const title = line.replace(/^#+\s*/, '');
        return <h4 key={idx} className="ai-chat-heading">{title}</h4>;
      }
      if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* ')) {
        const item = line.replace(/^[-•*]\s*/, '');
        return (
          <div key={idx} className="ai-chat-bullet">
            <span className="ai-bullet-dot">🌱</span>
            <span>{formatBold(item)}</span>
          </div>
        );
      }
      if (/^\d+\.\s/.test(line)) {
        return (
          <div key={idx} className="ai-chat-numbered">
            <span>{formatBold(line)}</span>
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: '6px' }} />;
      }
      return <p key={idx} className="ai-chat-paragraph">{formatBold(line)}</p>;
    });
  };

  const formatBold = (str) => {
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <>
      {/* Floating Action Button */}
      <button 
        className={`ai-chat-fab ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(prev => !prev)}
        title="Chat with AI Agronomist (LangChain & RAG)"
        aria-label="Open AI Agronomist Chat"
      >
        <span className="fab-icon">{isOpen ? '✕' : '🌾'}</span>
        {!isOpen && <span className="fab-badge">AI</span>}
      </button>

      {/* Slide-out / Modal Chat Window */}
      {isOpen && (
        <div className="ai-chat-window">
          {/* Header */}
          <div className="ai-chat-header">
            <div className="ai-header-left">
              <div className="ai-avatar">🤖</div>
              <div>
                <h3 className="ai-header-title">SmartAgri AI Agronomist</h3>
                <div className="ai-header-status">
                  <span className="status-indicator online"></span>
                  <span>LangChain RAG Knowledge Active</span>
                </div>
              </div>
            </div>
            <div className="ai-header-actions">
              <button className="ai-action-btn" onClick={clearChat} title="Clear Chat">
                🗑️
              </button>
              <button className="ai-action-btn" onClick={() => setIsOpen(false)} title="Close">
                ✕
              </button>
            </div>
          </div>

          {/* Quick suggestions */}
          <div className="ai-suggestions-row">
            {dynamicSuggestions.slice(0, 5).map((item, index) => {
              const text = item[lang] || item.en;
              return (
                <button
                  key={index}
                  className="ai-suggestion-chip"
                  onClick={() => handleSend(text)}
                  disabled={loading}
                >
                  {text}
                </button>
              );
            })}
          </div>

          {/* Messages list */}
          <div className="ai-messages-container">
            {messages.map((m) => (
              <div key={m.id} className={`ai-message-row ${m.role}`}>
                {m.role === 'assistant' && <div className="msg-avatar">🌾</div>}
                <div className={`ai-message-bubble ${m.role}`}>
                  {renderFormattedText(m.text)}
                  
                  {/* Sources tag if RAG retrieved context */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="ai-sources-tag">
                      <span className="source-label">📚 Verified Sources:</span>
                      {m.sources.map((src, i) => (
                        <span key={i} className="source-pill">{src}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="ai-message-row assistant">
                <div className="msg-avatar">🌾</div>
                <div className="ai-message-bubble assistant typing">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form 
            className="ai-chat-input-form"
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          >
            <button
              type="button"
              className={`ai-mic-btn ${listening ? 'listening' : ''}`}
              onClick={handleVoice}
              title={listening ? "Listening... click to stop" : "Speak your question"}
            >
              🎤
            </button>
            <input
              type="text"
              className="ai-chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={lang === 'hi' ? "फसल, परिणाम, खाद या रोग को समझाने के लिए पूछें..." : lang === 'kn' ? "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಫಲಿತಾಂಶ ಅಥವಾ ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ..." : "Ask to explain any result or agricultural question..."}
              disabled={loading}
            />
            <button
              type="submit"
              className="ai-send-btn"
              disabled={!input.trim() || loading}
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  );
}

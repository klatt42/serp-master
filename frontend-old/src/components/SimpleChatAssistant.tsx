import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function SimpleChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your SEO assistant. Ask me about:\n\n🔍 Keyword research\n⚡ Technical SEO audits\n✍️ Content optimization\n📊 SEO strategy\n\nHow can I help you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Simple keyword-based responses for now
      let response = '';

      const lowerInput = userMessage.toLowerCase();

      if (lowerInput.includes('keyword') || lowerInput.includes('research')) {
        response = "I can help you with keyword research! 🔍\n\nTo find the best keywords:\n1. Think about what your customers search for\n2. Use the Keyword Research panel above\n3. Look for keywords with good volume but lower competition\n\nTry entering a keyword like 'your business + service' in the research panel!";
      } else if (lowerInput.includes('audit') || lowerInput.includes('technical') || lowerInput.includes('speed')) {
        response = "Technical SEO is crucial! ⚡\n\nKey areas to check:\n• Page speed (aim for <3 seconds)\n• Mobile responsiveness\n• Core Web Vitals (LCP, FID, CLS)\n• SSL certificate\n• Schema markup\n\nUse the Technical Audit panel to scan your site!";
      } else if (lowerInput.includes('content') || lowerInput.includes('optimize') || lowerInput.includes('writing')) {
        response = "Content optimization tips: ✍️\n\n1. Use your target keyword naturally (1-2% density)\n2. Write compelling title tags (50-60 chars)\n3. Create unique meta descriptions with CTAs\n4. Use header hierarchy (H1, H2, H3)\n5. Add 2-3 internal links per page\n6. Aim for 1000+ words for competitive topics\n\nTry the Content Optimization panel above!";
      } else if (lowerInput.includes('rank') || lowerInput.includes('position')) {
        response = "Improving rankings takes time! 📈\n\nKey factors:\n1. Quality content that answers user intent\n2. Strong backlinks from relevant sites\n3. Fast, mobile-friendly site\n4. Regular content updates\n5. Good user experience (low bounce rate)\n\nFocus on creating the best content in your niche!";
      } else if (lowerInput.includes('discover') || lowerInput.includes('google discover')) {
        response = "Google Discover optimization! 🎯\n\nTo get featured:\n1. Use high-quality images (1200px+ width)\n2. Create fresh, timely content\n3. Set up RSS feed properly\n4. Add 'Follow' button to your site\n5. Focus on engaging, visual content\n\nDiscover reaches 1B+ users monthly!";
      } else if (lowerInput.includes('help') || lowerInput.includes('hi') || lowerInput.includes('hello')) {
        response = "Hello! 👋 I'm here to help with all your SEO needs.\n\nI can assist with:\n• Keyword research strategies\n• Technical SEO improvements\n• Content optimization tips\n• Link building advice\n• Google Discover optimization\n• General SEO strategy\n\nWhat would you like to know?";
      } else {
        response = `Great question about "${userMessage}"!\n\nFor SEO success, focus on:\n\n1. **Quality Content** - Answer user questions thoroughly\n2. **Technical Excellence** - Fast, mobile-friendly site\n3. **Authority** - Build quality backlinks\n4. **User Experience** - Easy navigation, good design\n5. **Regular Updates** - Keep content fresh\n\nWould you like specific advice on keywords, audits, or content optimization?`;
      }

      setTimeout(() => {
        setMessages(prev => [...prev, { role: 'assistant', content: response }]);
        setIsLoading(false);
      }, 500);

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I encountered an error. Please try asking again!"
      }]);
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center z-50"
        >
          <MessageSquare className="text-white" size={28} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <div>
              <h3 className="font-bold text-lg">SERP Master AI</h3>
              <p className="text-xs text-blue-100">Your SEO Assistant</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-white/20 rounded p-1 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask about SEO..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

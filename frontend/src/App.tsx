import { useState, useEffect } from 'react';
import { checkBackendHealth, sendChatMessage } from './services/api';
import AvatarCanvas from './components/avatarCanvas';
import ChatWindow from './components/chatWindow';
import type { AvatarEmotion, AvatarAnimation, ChatMessage } from './types/avatar';

const VALID_EMOTIONS: AvatarEmotion[] = ['neutral', 'happy', 'excited', 'grumpy', 'sad', 'thinking'];
const VALID_ANIMATIONS: AvatarAnimation[] = ['idle', 'talking', 'reacting'];

function toAvatarEmotion(value: string): AvatarEmotion {
  return (VALID_EMOTIONS as string[]).includes(value) ? (value as AvatarEmotion) : 'neutral';
}

function toAvatarAnimation(value: string): AvatarAnimation {
  return (VALID_ANIMATIONS as string[]).includes(value) ? (value as AvatarAnimation) : 'idle';
}

export default function App() {
  const [currentEmotion, setCurrentEmotion] = useState<AvatarEmotion>('neutral');
  const [currentAnimation, setCurrentAnimation] = useState<AvatarAnimation>('idle');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    checkBackendHealth()
      .then((data) => {
        if (data.status === 'online') setBackendStatus('connected');
      })
      .catch(() => setBackendStatus('disconnected'));
  }, []);

  const handleSend = async (text: string) => {
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    setCurrentAnimation('talking');

    try {
      const data = await sendChatMessage({ user_id: 'user_default', message: text });
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', text: data.response_text },
      ]);
      setCurrentEmotion(toAvatarEmotion(data.avatar_state.emotion));
      setCurrentAnimation(toAvatarAnimation(data.avatar_state.animation));
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          text: "I couldn't reach the server just now — mind trying again?",
        },
      ]);
      setCurrentAnimation('idle');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-md mx-auto p-4 bg-slate-900 border-x border-slate-800 shadow-2xl">
      {/* Header */}
      <header className="flex justify-between items-center py-2 border-b border-slate-800">
        <div>
          <h1 className="text-lg font-bold text-emerald-400">AI Companion</h1>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className={`w-2 h-2 rounded-full ${
              backendStatus === 'connected' ? 'bg-emerald-400 animate-pulse' :
              backendStatus === 'checking' ? 'bg-amber-400' : 'bg-rose-500'
            }`} />
            <span className="text-[10px] text-slate-400 uppercase tracking-wide">
              API: {backendStatus}
            </span>
          </div>
        </div>

        <div className="flex gap-2">
          <span className="text-xs px-2.5 py-1 bg-slate-800 rounded-full text-slate-400 font-mono uppercase">
            {currentEmotion}
          </span>
          <span className="text-xs px-2.5 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-full font-mono uppercase">
            {currentAnimation}
          </span>
        </div>
      </header>

      {/* 2D Avatar Canvas Viewport */}
      <div className="flex flex-col items-center border-b border-slate-800 py-2">
        <AvatarCanvas
          emotion={currentEmotion}
          animation={currentAnimation}
          width={144}
          height={144}
        />

        <details className="w-full">
          <summary className="text-[10px] uppercase tracking-wider text-slate-500 text-center cursor-pointer select-none py-1">
            Dev controls
          </summary>
          <div className="flex flex-col items-center gap-2 pb-2">
            <div className="flex gap-2">
              {(['idle', 'talking', 'reacting'] as const).map((anim) => (
                <button
                  key={anim}
                  onClick={() => setCurrentAnimation(anim)}
                  className={`px-2.5 py-1 text-[11px] rounded-lg font-medium transition cursor-pointer ${
                    currentAnimation === anim
                      ? 'bg-emerald-500 text-slate-950 font-bold shadow'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {anim}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {(['neutral', 'happy', 'grumpy', 'excited', 'sad', 'thinking'] as const).map((emo) => (
                <button
                  key={emo}
                  onClick={() => setCurrentEmotion(emo)}
                  className={`px-2.5 py-1 text-[11px] rounded-lg font-medium transition cursor-pointer ${
                    currentEmotion === emo
                      ? 'bg-sky-500 text-slate-950 font-bold shadow'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {emo}
                </button>
              ))}
            </div>
          </div>
        </details>
      </div>

      {/* Chat message stream */}
      <ChatWindow messages={messages} isSending={isSending} onSend={handleSend} />
    </div>
  );
}

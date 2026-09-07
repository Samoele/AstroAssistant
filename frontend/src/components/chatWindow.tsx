import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import type { ChatMessage } from '../types/avatar';

interface ChatWindowProps {
  messages: ChatMessage[];
  isSending: boolean;
  onSend: (text: string) => void;
}

export default function ChatWindow({ messages, isSending, onSend }: ChatWindowProps) {
  const [draft, setDraft] = useState('');
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to the newest message (and to the typing indicator while waiting)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isSending]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || isSending) return;
    onSend(trimmed);
    setDraft('');
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-1 py-2 flex flex-col gap-2">
        {messages.length === 0 && (
          <p className="text-center text-xs text-slate-500 mt-6">
            Say hi to your companion to get started.
          </p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm leading-snug break-words ${
              msg.role === 'user'
                ? 'self-end bg-emerald-500 text-slate-950 font-medium rounded-br-sm'
                : 'self-start bg-slate-800 text-slate-100 rounded-bl-sm'
            }`}
          >
            {msg.text}
          </div>
        ))}
        {isSending && (
          <div
            className="self-start bg-slate-800 text-slate-400 rounded-2xl rounded-bl-sm px-3.5 py-2.5"
            aria-label="Companion is typing"
          >
            <span className="inline-flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
            </span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex gap-2 pt-2"
        style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
      >
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Talk to your companion..."
          enterKeyHint="send"
          autoComplete="off"
          // text-base (16px) keeps iOS Safari from auto-zooming the page on focus
          className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-base text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
        />
        <button
          type="submit"
          disabled={isSending || !draft.trim()}
          className="bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-bold px-4 rounded-xl text-sm hover:bg-emerald-400 transition cursor-pointer touch-manipulation min-w-16"
        >
          Send
        </button>
      </form>
    </div>
  );
}

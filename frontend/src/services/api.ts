import type { ChatRequest,  ChatMessage, ChatHistoryMessage, AgentResponse } from '../types/avatar';

const API_BASE_URL = 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  service: string;
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Server returned HTTP status ${response.status}`);
  }
  return response.json();
}

export async function fetchChatHistory(userId = 'user_default'): Promise<ChatMessage[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/history?user_id=${encodeURIComponent(userId)}`);
  if (!response.ok) {
    throw new Error(`Failed to load history: ${response.statusText}`);
  }

  // The backend returns: [{ id: "1", role: "user", text: "...", emotion: "..." }, ...]
  const rawData: Array<{ id: string | number; role: 'user' | 'assistant'; text: string }> = await response.json();

  return rawData.map((item) => ({
    id: String(item.id),
    role: item.role,
    text: item.text,
  }));
}

export async function sendChatMessage(
  message: string,
  userId = 'user_default'
): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.statusText}`);
  }

  return response.json();
}
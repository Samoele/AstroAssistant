import type { ChatRequest, AgentResponse } from '../types/avatar';

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

export async function sendChatMessage(message: string, userId = 'default_user'): Promise<AgentResponse> {
  const payload: ChatRequest = {
    user_id: userId,
    message,
  };

  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.statusText}`);
  }

  return response.json();
}
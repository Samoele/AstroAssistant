/**
 * Emotional mood states mirroring Python's EmotionEnum in schemas.py
 */
export type AvatarEmotion = 
  | 'neutral'
  | 'happy'
  | 'excited'
  | 'grumpy'
  | 'sad'
  | 'thinking';

/**
 * Kinetic movement states mirroring Python's AnimationStateEnum
 */
export type AvatarAnimation = 
  | 'idle'
  | 'talking'
  | 'reacting';

/**
 * Avatar visual state container
 */
export interface AvatarState {
  emotion: AvatarEmotion;
  animation: AvatarAnimation;
  mood_reason?: string;
}

/**
 * A single message in the conversation history sent to the backend
 */
export interface ChatHistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Outgoing message payload to backend
 */
export interface ChatRequest {
  user_id: string;
  message: string;
  history: ChatHistoryMessage[];
}

/**
 * Structured response payload from backend
 */
export interface AgentResponse {
  response_text: string;
  avatar_state: AvatarState;
  suggested_actions: string[];
}

/**
 * A single rendered bubble in the chat message stream
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}
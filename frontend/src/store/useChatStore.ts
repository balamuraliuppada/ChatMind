import { create } from 'zustand';
import { Socket } from 'socket.io-client';

export interface Participant {
  id: string;
  display_name: string;
}

export interface Message {
  id: string;
  room_id: string;
  sender_id: string;
  sender_name?: string;
  message: string;
  created_at: string;
}

interface ChatState {
  socket: Socket | null;
  setSocket: (socket: Socket | null) => void;
  
  participants: Participant[];
  setParticipants: (participants: Participant[]) => void;
  addParticipant: (participant: Participant) => void;
  removeParticipant: (id: string) => void;
  
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  
  roomCode: string | null;
  setRoomCode: (code: string | null) => void;
  
  currentUserId: string | null;
  setCurrentUserId: (id: string | null) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  socket: null,
  setSocket: (socket) => set({ socket }),
  
  participants: [],
  setParticipants: (participants) => set({ participants }),
  addParticipant: (participant) => set((state) => ({ 
    participants: [...state.participants.filter(p => p.id !== participant.id), participant] 
  })),
  removeParticipant: (id) => set((state) => ({ 
    participants: state.participants.filter(p => p.id !== id) 
  })),
  
  messages: [],
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  
  roomCode: null,
  setRoomCode: (roomCode) => set({ roomCode }),
  
  currentUserId: null,
  setCurrentUserId: (currentUserId) => set({ currentUserId }),
}));

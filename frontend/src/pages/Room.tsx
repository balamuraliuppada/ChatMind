import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Copy, LogOut, Send } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../services/api';
import { useChatStore } from '../store/useChatStore';
import clsx from 'clsx';

export default function Room() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [msgInput, setMsgInput] = useState('');
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    socket, setSocket,
    messages, setMessages, addMessage,
    addParticipant, removeParticipant, setParticipants,
    roomCode, setRoomCode,
    currentUserId, setCurrentUserId,
    participants
  } = useChatStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingUsers]);

  useEffect(() => {
    let newSocket: any = null;
    const initRoom = async () => {
      try {
        const { data: roomData } = await api.get('/rooms/me');
        if (roomData.room.id !== roomId) {
          navigate('/');
          return;
        }
        setRoomCode(roomData.room.room_code);
        setCurrentUserId(roomData.participant.id);
        
        const { data: initialMessages } = await api.get(`/rooms/${roomId}/messages`);
        setMessages(initialMessages);

        const { data: initialParticipants } = await api.get(`/rooms/${roomId}/participants`);
        setParticipants(initialParticipants);

        let socketUrl = import.meta.env.VITE_SOCKET_URL || 
                          (import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/api\/v1\/?$/, '') : 'http://localhost:8000');
        if (socketUrl.endsWith('/')) {
          socketUrl = socketUrl.slice(0, -1);
        }
        
        // Convert http/https to ws/wss
        const wsUrl = socketUrl.replace(/^http/, 'ws');
        const token = localStorage.getItem('chatminds_token');
        
        // Connect Socket
        newSocket = new WebSocket(`${wsUrl}/ws?token=${token}`);

        newSocket.onopen = () => {
          console.log('Connected to socket');
          setIsConnected(true);
        };

        newSocket.onclose = () => {
          console.log('Disconnected from socket');
          setIsConnected(false);
        };

        newSocket.onerror = (error: any) => {
          console.error('Socket error:', error);
          setIsConnected(false);
        };

        newSocket.onmessage = (event: MessageEvent) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'user_joined') {
              addParticipant({ id: data.participant_id, display_name: data.display_name });
            } else if (data.type === 'user_left') {
              removeParticipant(data.participant_id);
            } else if (data.type === 'new_message') {
              console.log('Received new_message:', data);
              addMessage(data);
            } else if (data.type === 'typing') {
              if (data.is_typing) {
                setTypingUsers(prev => prev.includes(data.display_name) ? prev : [...prev, data.display_name]);
              } else {
                setTypingUsers(prev => prev.filter(name => name !== data.display_name));
              }
            }
          } catch (e) {
            console.error('Failed to parse socket message', e);
          }
        };

        setSocket(newSocket);
        setLoading(false);
      } catch (err) {
        console.error(err);
        navigate('/');
      }
    };

    initRoom();

    return () => {
      if (newSocket) {
        newSocket.close();
      }
      setSocket(null);
    };
  }, [roomId]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!msgInput.trim() || !socket || !currentUserId || !roomId) return;
    
    const msgId = crypto.randomUUID();
    
    // Optimistic UI Update
    addMessage({
      id: msgId,
      room_id: roomId,
      sender_id: currentUserId,
      sender_name: "You",
      message: msgInput.trim(),
      created_at: new Date().toISOString()
    });
    
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'message',
        id: msgId,
        message: msgInput.trim()
      }));
      
      socket.send(JSON.stringify({
        type: 'typing',
        is_typing: false
      }));
    }
    setMsgInput('');
  };

  let typingTimer: ReturnType<typeof setTimeout>;
  const handleTyping = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMsgInput(e.target.value);
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    
    socket.send(JSON.stringify({ type: 'typing', is_typing: true }));
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
      }
    }, 1500);
  };

  const copyCode = () => {
    if (roomCode) {
      navigator.clipboard.writeText(roomCode);
      // Optional: add toast
    }
  };

  const handleLeave = async () => {
    localStorage.removeItem('chatminds_token');
    try {
      await api.post('/rooms/leave');
    } catch (e) {}
    navigate('/');
  };

  if (loading) {
    return <div className="flex-1 flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="flex-1 min-h-0 flex flex-col h-full max-h-full overflow-hidden max-w-4xl mx-auto w-full">
      {/* Top Header */}
      <div className="bg-panel border-b border-white/10 p-4 flex items-center justify-between z-20">
        <div>
          <h2 className="font-bold text-xl text-white mb-1">ChatMinds</h2>
          <div className="flex items-center gap-2 text-xs font-medium">
            <span className="text-slate-400">Code:</span>
            <span className="text-primary tracking-widest">{roomCode}</span>
            <button onClick={copyCode} className="text-slate-500 hover:text-white transition-colors">
              <Copy size={12} />
            </button>
            <span className="mx-2 text-slate-700">|</span>
            <div className="flex items-center gap-1.5">
              <div className={clsx("w-2 h-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)]", isConnected ? "bg-green-500 shadow-green-500/50" : "bg-red-500 shadow-red-500/50")}></div>
              <span className={isConnected ? "text-green-400" : "text-red-400"}>
                {isConnected ? "Connected" : "Disconnected"}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex -space-x-2 mr-2">
            {participants.map((p: any) => (
              <div key={p.id} className="w-8 h-8 rounded-full border-2 border-panel bg-primary/20 flex items-center justify-center text-primary font-bold text-xs" title={p.display_name}>
                {p.display_name.charAt(0).toUpperCase()}
              </div>
            ))}
          </div>
          <button onClick={handleLeave} className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium">
            <LogOut size={16} /> <span className="hidden sm:inline">Leave</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 min-h-0 flex flex-col bg-darker/30 relative">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {messages.map((msg, i) => {
            const isMe = msg.sender_id === currentUserId;
            const showName = i === 0 || messages[i-1].sender_id !== msg.sender_id;
            
            return (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={msg.id} 
                className={clsx("flex flex-col max-w-[80%]", isMe ? "ml-auto items-end" : "mr-auto items-start")}
              >
                {!isMe && showName && (
                  <span className="text-xs text-slate-400 ml-1 mb-1 font-medium">{msg.sender_name}</span>
                )}
                <div 
                  className={clsx(
                    "px-4 py-2 rounded-2xl",
                    isMe 
                      ? "bg-primary text-white rounded-tr-sm" 
                      : "bg-panel border border-white/10 text-slate-200 rounded-tl-sm"
                  )}
                >
                  <p className="break-words">{msg.message}</p>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 mx-1">
                  {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </motion.div>
            );
          })}
          
          {typingUsers.length > 0 && (
            <div className="text-xs text-slate-400 italic px-2">
              {typingUsers.join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-panel/50 border-t border-white/10 backdrop-blur-md">
          <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto relative">
            <input 
              type="text" 
              value={msgInput}
              onChange={handleTyping}
              placeholder="Type a message..."
              className="flex-1 bg-darker/80 border border-slate-700 rounded-full px-6 py-3 text-slate-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
            />
            <button 
              type="submit"
              disabled={!msgInput.trim()}
              className="absolute right-2 top-2 bottom-2 aspect-square bg-primary hover:bg-secondary text-white rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:hover:bg-primary"
            >
              <Send size={18} className="ml-0.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

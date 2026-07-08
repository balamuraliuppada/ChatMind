import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import { Copy, LogOut, Send } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../services/api';
import { useChatStore } from '../store/useChatStore';
import clsx from 'clsx';

export default function Room() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [msgInput, setMsgInput] = useState('');
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    socket, setSocket,
    messages, setMessages, addMessage,
    addParticipant, removeParticipant,
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

        // Connect Socket
        newSocket = io(import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000', {
          path: '/socket.io/',
          withCredentials: true,
          auth: {
            token: localStorage.getItem('chatminds_token')
          }
        });

        newSocket.on('connect', () => {
          console.log('Connected to socket');
        });

        newSocket.on('user_joined', (user: any) => {
          addParticipant({ id: user.participant_id, display_name: user.display_name });
        });

        newSocket.on('user_left', (user: any) => {
          removeParticipant(user.participant_id);
        });

        newSocket.on('new_message', (msg: any) => {
          addMessage(msg);
        });

        newSocket.on('user_typing', (data: any) => {
          if (data.is_typing) {
            setTypingUsers(prev => prev.includes(data.display_name) ? prev : [...prev, data.display_name]);
          } else {
            setTypingUsers(prev => prev.filter(name => name !== data.display_name));
          }
        });

        setSocket(newSocket);
        setLoading(false);
      } catch (err) {
        console.error(err);
        navigate('/');
      }
    };

    initRoom();

    return () => {
      if (newSocket) newSocket.disconnect();
    };
  }, [roomId]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!msgInput.trim() || !socket) return;
    
    socket.emit('message', { message: msgInput.trim() });
    setMsgInput('');
    socket.emit('typing', { is_typing: false });
  };

  let typingTimer: ReturnType<typeof setTimeout>;
  const handleTyping = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMsgInput(e.target.value);
    if (!socket) return;
    
    socket.emit('typing', { is_typing: true });
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      socket.emit('typing', { is_typing: false });
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
    <div className="flex-1 flex flex-col h-screen max-w-4xl mx-auto w-full">
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
              <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
              <span className="text-green-400">Connected</span>
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
      <div className="flex-1 flex flex-col min-w-0 bg-darker/30 relative">
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

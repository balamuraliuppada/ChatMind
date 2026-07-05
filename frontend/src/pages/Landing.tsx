import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, Plus } from 'lucide-react';
import api from '../services/api';

export default function Landing() {
  const navigate = useNavigate();
  const [isJoin, setIsJoin] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!displayName) {
      setError('Display name is required');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      if (isJoin) {
        if (!roomCode || roomCode.length !== 6) {
          setError('Valid 6-character room code required');
          setLoading(false);
          return;
        }
        const res = await api.post('/rooms/join', { room_code: roomCode, display_name: displayName });
        navigate(`/room/${res.data.room.id}`);
      } else {
        const res = await api.post('/rooms', { display_name: displayName });
        navigate(`/room/${res.data.room.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-2xl w-full max-w-md p-8 relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-blue-500" />
        
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
            ChatMinds
          </h1>
          <p className="text-slate-400">Anonymous, temporary, secure.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Display Name</label>
            <input 
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full bg-darker/50 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              placeholder="How should others call you?"
              maxLength={50}
            />
          </div>

          {isJoin && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
            >
              <label className="block text-sm font-medium text-slate-300 mb-1">Room Code</label>
              <input 
                type="text"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                className="w-full bg-darker/50 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors uppercase"
                placeholder="6-Character Code"
                maxLength={6}
              />
            </motion.div>
          )}

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-400/10 py-2 rounded-lg">
              {error}
            </div>
          )}

          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-secondary text-white font-medium rounded-lg px-4 py-3 flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : isJoin ? (
              <><LogIn size={18} /> Join Room</>
            ) : (
              <><Plus size={18} /> Create Room</>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button 
            onClick={() => setIsJoin(!isJoin)}
            className="text-slate-400 hover:text-white transition-colors text-sm"
          >
            {isJoin ? "Want to start a new chat? Create a room." : "Have a code? Join a room."}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

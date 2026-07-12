import { useState } from 'react';
import axios from 'axios';
import { Settings, X, Save, Key, ShieldCheck } from 'lucide-react';

export function SettingsModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [clientId, setClientId] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!clientId || !accessToken) {
      setMessage({ text: 'Please fill in both fields', type: 'error' });
      return;
    }
    
    setLoading(true);
    setMessage(null);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await axios.post(`${API_URL}/api/v1/settings/token`, {
        client_id: clientId,
        access_token: accessToken
      });
      setMessage({ text: 'Token updated successfully in memory!', type: 'success' });
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      setMessage({ text: 'Failed to update token.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#18181b] border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-200 flex items-center gap-2">
            <Settings size={20} className="text-blue-400" /> API Settings
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-gray-400">Update your Dhan API credentials dynamically without restarting the server.</p>
          
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Client ID</label>
            <div className="relative">
              <Key size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input 
                type="text" 
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="Enter Dhan Client ID" 
                className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Access Token</label>
            <div className="relative">
              <ShieldCheck size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input 
                type="password" 
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                placeholder="Paste new daily token" 
                className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>
          </div>
        </div>

        {message && (
          <div className={`mt-4 p-3 rounded-lg text-sm flex items-center gap-2 ${message.type === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
            {message.text}
          </div>
        )}

        <div className="mt-8 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 transition-colors">
            Cancel
          </button>
          <button 
            onClick={handleSave} 
            disabled={loading}
            className="px-4 py-2 rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            {loading ? 'Saving...' : <><Save size={16} /> Save Credentials</>}
          </button>
        </div>
      </div>
    </div>
  );
}

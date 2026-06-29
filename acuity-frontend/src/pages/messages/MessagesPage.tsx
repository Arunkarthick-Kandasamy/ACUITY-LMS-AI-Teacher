import { useState, useEffect } from 'react';
import { apiRequest } from '../../services/api';

interface Conversation {
  conversation_id: string;
  other_participant_name: string;
  last_message: string;
  last_message_at: string | null;
  unread_count: number;
}

interface Message {
  message_id: string;
  sender_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

const MessagesPage = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConv, setSelectedConv] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMsg, setNewMsg] = useState('');
  const [receiverId, setReceiverId] = useState('');
  const [activeTab, setActiveTab] = useState<'inbox' | 'new'>('inbox');

  useEffect(() => {
    apiRequest('/messaging/conversations').then((res: any) => {
      setConversations(res?.data || []);
    }).catch(() => {});
  }, []);

  const openConversation = async (convId: string) => {
    setSelectedConv(convId);
    const res: any = await apiRequest(`/messaging/conversations/${convId}`);
    setMessages(res?.data || []);
  };

  const sendMessage = async () => {
    if (!newMsg.trim()) return;
    if (activeTab === 'new' && !receiverId) return;
    const payload = activeTab === 'new'
      ? { receiver_id: receiverId, content: newMsg }
      : { receiver_id: '', content: newMsg };
    await apiRequest('/messaging/send', { method: 'POST', body: JSON.stringify(payload) });
    setNewMsg('');
    if (selectedConv) openConversation(selectedConv);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      <div className="w-80 border-r bg-white p-4 overflow-y-auto">
        <div className="flex mb-4 gap-2">
          <button onClick={() => setActiveTab('inbox')} className={`px-3 py-1 rounded ${activeTab === 'inbox' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>Inbox</button>
          <button onClick={() => setActiveTab('new')} className={`px-3 py-1 rounded ${activeTab === 'new' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>New</button>
        </div>
        {activeTab === 'inbox' ? (
          conversations.map((c) => (
            <div key={c.conversation_id} onClick={() => openConversation(c.conversation_id)} className={`p-3 mb-2 rounded cursor-pointer ${selectedConv === c.conversation_id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'}`}>
              <div className="font-medium">{c.other_participant_name}</div>
              <div className="text-sm text-gray-500 truncate">{c.last_message}</div>
              {c.unread_count > 0 && <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">{c.unread_count}</span>}
            </div>
          ))
        ) : (
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Recipient ID"
              value={receiverId}
              onChange={(e) => setReceiverId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        )}
      </div>
      <div className="flex-1 flex flex-col bg-gray-50">
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {(activeTab === 'inbox' ? messages : []).map((m) => (
            <div key={m.message_id} className={`p-3 rounded-lg max-w-[70%] ${m.sender_id === 'me' ? 'ml-auto bg-blue-600 text-white' : 'bg-white border'}`}>
              <p>{m.content}</p>
              <span className="text-xs opacity-70">{new Date(m.created_at).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
        <div className="p-4 border-t bg-white flex gap-3">
          <input
            type="text"
            value={newMsg}
            onChange={(e) => setNewMsg(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <button onClick={sendMessage} className="px-4 py-2 bg-blue-600 text-white rounded-lg">Send</button>
        </div>
      </div>
    </div>
  );
};

export default MessagesPage;

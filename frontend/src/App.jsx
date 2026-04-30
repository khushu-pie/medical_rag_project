import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { UploadCloud, Image as ImageIcon, Send, FileText, Activity, Trash2 } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setUploadedFiles(prev => [...prev, file.name]);
    } catch (error) {
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('query', userMessage);

      const response = await axios.post('http://localhost:8000/query', formData);
      setMessages(prev => [...prev, { text: response.data.answer, sender: 'bot' }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: `Error: ${error.response?.data?.detail || error.message}\n\nThis is not a substitute for professional medical advice`, sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    if (!window.confirm("Are you sure you want to wipe all stored documents and start fresh?")) return;
    
    setIsLoading(true);
    try {
      await axios.post('http://localhost:8000/clear');
      setUploadedFiles([]);
      setMessages([]);
      alert("Database wiped successfully. You can now start fresh!");
    } catch (error) {
      alert(`Clear failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1><span>Health</span>RAG</h1>
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', color: '#64748b'}}>
          <Activity size={20} />
          <span style={{fontWeight: 500}}>Medical Q&A System</span>
        </div>
      </div>
      
      <div className="content-area">
        <div className="upload-panel">
          <h2>Document & Image Upload</h2>
          <div className="upload-zone" onClick={handleUploadClick}>
            {isUploading ? (
              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px'}}>
                <div className="spinner dark"></div>
                <span style={{fontSize: '0.9rem', color: '#64748b'}}>Processing...</span>
              </div>
            ) : (
              <>
                <UploadCloud className="upload-icon" />
                <p className="upload-text">Click to upload PDF, JPG, or PNG</p>
              </>
            )}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
              accept=".pdf,.jpg,.jpeg,.png"
            />
          </div>
          
          <h3 style={{margin: '0', fontSize: '1.1rem', fontWeight: 600}}>Uploaded Files</h3>
          <ul className="file-list">
            {uploadedFiles.map((file, idx) => (
              <li key={idx} className="file-item">
                {file.toLowerCase().endsWith('.pdf') ? <FileText size={16} color="#2563eb"/> : <ImageIcon size={16} color="#10b981"/>}
                <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{file}</span>
              </li>
            ))}
            {uploadedFiles.length === 0 && (
              <li style={{fontSize: '0.85rem', color: '#94a3b8', padding: '12px 0'}}>No files uploaded yet.</li>
            )}
          </ul>
          
          <button 
            onClick={handleClear} 
            style={{marginTop: '15px', width: '100%', padding: '10px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: 500, opacity: isLoading ? 0.7 : 1}}
            disabled={isLoading}
          >
            <Trash2 size={16} /> Wipe Database
          </button>
        </div>
        
        <div className="chat-panel">
          <div className="chat-history">
            {messages.length === 0 && (
              <div style={{margin: 'auto', textAlign: 'center', color: '#94a3b8', maxWidth: '400px'}}>
                <Activity size={48} style={{margin: '0 auto 16px', opacity: 0.5, color: '#2563eb'}} />
                <h3 style={{color: '#1e293b'}}>Welcome to HealthRAG</h3>
                <p>Upload your medical documents or images on the left, then ask questions about them in plain English.</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender}`}>
                {msg.sender === 'bot' ? (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                  msg.text
                )}
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                  <div className="spinner dark"></div>
                  <span style={{color: '#64748b'}}>Analyzing documents...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          <form className="input-area" onSubmit={handleSendMessage}>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents... (e.g., What does my creatinine level mean?)"
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
      
      <div className="disclaimer">
        WARNING: This is not a substitute for professional medical advice. Always consult with a qualified healthcare provider.
      </div>
    </div>
  );
}

export default App;

import React, { useState } from 'react';
import { Menu, X, Activity } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { AnalyzeView } from './components/AnalyzeView';
import { MethodologyView } from './components/MethodologyView';
import { SystemHealth } from './components/SystemHealth';
import { analyzeChatLog } from './services/api';

function App() {
  const [activeView, setActiveView] = useState('analyze');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const closeSidebar = () => setIsSidebarOpen(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResults(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeChatLog(file);
      setResults(data.results);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze file. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const renderView = () => {
    switch(activeView) {
      case 'analyze':
        return <AnalyzeView 
                  file={file} 
                  onFileChange={handleFileChange} 
                  onUpload={handleUpload} 
                  loading={loading} 
                  error={error} 
                  results={results} 
                />;
      case 'methodology':
        return <MethodologyView />;
      case 'health':
        return <SystemHealth />;
      default:
        return <AnalyzeView />;
    }
  };

  const handleViewChange = (view) => {
    setActiveView(view);
    closeSidebar();
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-bg-primary)' }}>
      {/* Mobile Header */}
      <header className="mobile-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ padding: '4px', borderRadius: '6px', background: 'var(--color-accent-primary)' }}>
            <Activity size={16} color="white" />
          </div>
          <span style={{ fontWeight: 700, fontSize: '1rem' }}>Subtext AI</span>
        </div>
        <button 
          onClick={toggleSidebar}
          style={{ background: 'transparent', border: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }}
        >
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Sidebar Overlay */}
      <div 
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`} 
        onClick={closeSidebar}
      />

      <Sidebar 
        activeView={activeView} 
        onViewChange={handleViewChange} 
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
      />
      
      <main className="main-content" style={{ 
        flex: 1, 
        paddingBottom: '4rem',
        minHeight: '100vh',
        overflowY: 'auto'
      }}>
        {renderView()}
      </main>
    </div>
  );
}

export default App;

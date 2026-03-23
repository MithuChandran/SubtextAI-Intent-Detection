import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { AnalyzeView } from './components/AnalyzeView';
import { MethodologyView } from './components/MethodologyView';
import { SystemHealth } from './components/SystemHealth';
import { analyzeChatLog } from './services/api';

function App() {
  const [activeView, setActiveView] = useState('analyze');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

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

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-bg-primary)' }}>
      <Sidebar activeView={activeView} onViewChange={setActiveView} />
      
      <main style={{ 
        flex: 1, 
        marginLeft: '280px', // Allow space for sidebar
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

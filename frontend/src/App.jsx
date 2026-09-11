import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardPage } from './pages/DashboardPage';
import { ChatPage } from './pages/ChatPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { AgentTasksPage } from './pages/AgentTasksPage';
import { ModelsPage } from './pages/ModelsPage';
import { GeneratedFilesPage } from './pages/GeneratedFilesPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const location = useLocation();

  // Helper to map route path to header title
  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/':
        return 'Dashboard & Operations';
      case '/chat':
        return 'Confidential Industrial AI Chat';
      case '/documents':
        return 'Confidential Documents';
      case '/knowledge':
        return 'Local RAG Knowledge Base';
      case '/agents':
        return 'Autonomous Agentic Workflows';
      case '/models':
        return 'Local Open-Weight Model Registry';
      case '/files':
        return 'Generated Deliverables Repository';
      case '/settings':
        return 'System & On-Premise Settings';
      default:
        return 'Sovereign AI Workbench';
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0b0f17] text-slate-100 font-sans">
      {/* Left Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <Header title={getPageTitle(location.pathname)} />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-[#0b0f17]">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/knowledge" element={<KnowledgeBasePage />} />
            <Route path="/agents" element={<AgentTasksPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/files" element={<GeneratedFilesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;

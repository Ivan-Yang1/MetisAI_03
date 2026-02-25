import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import AgentsPage from './pages/AgentsPage';
import ConversationsPage from './pages/ConversationsPage';
import MessagesPage from './pages/MessagesPage';
import Layout from './components/Layout';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<AgentsPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/conversations" element={<ConversationsPage />} />
          <Route path="/conversations/:id/messages" element={<MessagesPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

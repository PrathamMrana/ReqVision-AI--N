import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ProjectWorkspace from './pages/ProjectWorkspace';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col font-sans">
        <Toaster position="top-right" toastOptions={{ style: { background: "rgba(255, 255, 255, 0.05)", backdropFilter: "blur(20px)", color: "#ffffff", border: "1px solid rgba(255, 255, 255, 0.2)", borderRadius: "1rem", color: "#e2e8f0", border: "1px solid #1e293b", boxShadow: "0 0 15px rgba(0,243,255,0.2)" } }} />
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/workspace" element={<ProjectWorkspace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;

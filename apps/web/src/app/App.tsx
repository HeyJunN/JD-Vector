import { Routes, Route } from 'react-router-dom';
import './App.css';
import Header from '@/components/layout/Header';
import UploadPage from '@/pages/UploadPage';

// Pages (will be implemented later)
// import HomePage from '@/pages/HomePage';
// import AnalysisPage from '@/pages/AnalysisPage';
// import ResultPage from '@/pages/ResultPage';
// import RoadmapPage from '@/pages/RoadmapPage';
// import NotFoundPage from '@/pages/NotFoundPage';

function App() {
  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/upload" element={<UploadPage />} />
        {/* Additional routes will be added here */}
        {/* <Route path="/analysis" element={<AnalysisPage />} /> */}
        {/* <Route path="/result" element={<ResultPage />} /> */}
        {/* <Route path="/roadmap" element={<RoadmapPage />} /> */}
      </Routes>
    </div>
  );
}

export default App;

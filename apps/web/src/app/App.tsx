import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './App.css';
import Header from '@/components/layout/Header';
import UploadPage from '@/pages/UploadPage';
import AnalysisPage from '@/pages/AnalysisPage';
import RoadmapPage from '@/pages/RoadmapPage';

// Pages (will be implemented later)
// import HomePage from '@/pages/HomePage';
// import ResultPage from '@/pages/ResultPage';
// import NotFoundPage from '@/pages/NotFoundPage';

function App() {
  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
        {/* Additional routes will be added here */}
        {/* <Route path="/result" element={<ResultPage />} /> */}
      </Routes>

      {/* Toast Notifications - Dark Mode Optimized */}
      <Toaster
        position="top-right"
        toastOptions={{
          // 기본 스타일 - Slate-950 다크 모드 디자인
          duration: 4000,
          style: {
            background: '#0f172a', // slate-900
            color: '#f1f5f9', // slate-100
            border: '1px solid #334155', // slate-700
            borderRadius: '0.75rem', // rounded-xl
            padding: '1rem',
            fontSize: '0.875rem', // text-sm
            fontWeight: '500',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
          },
          // 성공 토스트
          success: {
            iconTheme: {
              primary: '#10b981', // emerald-500
              secondary: '#f1f5f9', // slate-100
            },
            style: {
              border: '1px solid #059669', // emerald-600
            },
          },
          // 에러 토스트
          error: {
            iconTheme: {
              primary: '#ef4444', // red-500
              secondary: '#f1f5f9', // slate-100
            },
            style: {
              border: '1px solid #dc2626', // red-600
            },
          },
          // 로딩 토스트
          loading: {
            iconTheme: {
              primary: '#3b82f6', // blue-500
              secondary: '#f1f5f9', // slate-100
            },
            style: {
              border: '1px solid #2563eb', // blue-600
            },
          },
        }}
      />
    </div>
  );
}

export default App;

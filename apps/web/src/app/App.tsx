import { Routes, Route } from 'react-router-dom';
import './App.css';

// Pages (will be implemented later)
// import HomePage from '@/pages/HomePage';
// import UploadPage from '@/pages/UploadPage';
// import AnalysisPage from '@/pages/AnalysisPage';
// import ResultPage from '@/pages/ResultPage';
// import RoadmapPage from '@/pages/RoadmapPage';
// import NotFoundPage from '@/pages/NotFoundPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            JD-Vector
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            AI 기반 직무 적합도 분석 및 커리어 로드맵 서비스
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <div className="text-center py-20">
                <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  환영합니다!
                </h2>
                <p className="text-lg text-gray-600 dark:text-gray-400">
                  JD-Vector 프로젝트 초기 설정이 완료되었습니다.
                </p>
                <p className="text-md text-gray-500 dark:text-gray-500 mt-4">
                  Frontend 개발을 시작하세요!
                </p>
              </div>
            }
          />
          {/* Additional routes will be added here */}
        </Routes>
      </main>

      <footer className="mt-auto bg-white dark:bg-gray-800 shadow-inner">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            © 2024 JD-Vector. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

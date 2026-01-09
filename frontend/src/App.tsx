/**
 * Main Application Component
 */
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SimulationProvider } from './contexts/SimulationContext';
import SimulationBuilder from './components/SimulationBuilder/SimulationBuilder';
import SimulationRunner from './components/SimulationRunner/SimulationRunner';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

function Header() {
  const location = useLocation();
  const isBuilder = location.pathname === '/';
  const isRunner = location.pathname === '/runner';

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">
              Concordia
            </h1>
            <nav className="flex space-x-1">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isBuilder
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                Builder
              </Link>
              <Link
                to="/runner"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isRunner
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                Runner
              </Link>
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SimulationProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            <Header />

            <main className="flex-1 max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 w-full mb-16">
              <Routes>
                <Route path="/" element={<SimulationBuilder />} />
                <Route path="/runner" element={<SimulationRunner />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 z-50">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Simulation Engine v1.1.0 | Built on Google DeepMind Concordia</span>
                  <span>Developed by Ng Chong</span>
                </div>
              </div>
            </footer>
          </div>
        </BrowserRouter>
      </SimulationProvider>
    </QueryClientProvider>
  );
}

export default App;

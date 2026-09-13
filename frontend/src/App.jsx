import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import HomePage from './pages/HomePage';
import ProcesoPage from './pages/ProcesoPage';
import LoginPage from './pages/LoginPage';
import StatsBoard from './components/dashboard/StatsBoard';
import Header from './components/layout/Header';
import ContadoresPage from './pages/ContadoresPage';
import ContadorDetallePage from './pages/ContadorDetallePage';
import LiquidacionPage from './pages/LiquidacionPage';
import CalculadoraImpuestosPage from './pages/CalculadoraImpuestosPage';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-sire-dark flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, rol } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-sire-dark flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (rol !== 'ADMIN') {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppRoutes() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const showHeader = isAuthenticated && location.pathname !== '/login';

  return (
    <div className="min-h-screen bg-sire-dark flex flex-col">
      {showHeader && <Header />}
      <div className="flex-grow">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><StatsBoard /></ProtectedRoute>} />
          <Route path="/proceso" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/proceso/:sesionId" element={<ProtectedRoute><ProcesoPage /></ProtectedRoute>} />
          <Route path="/admin/contadores" element={<AdminRoute><ContadoresPage /></AdminRoute>} />
          <Route path="/admin/contadores/:id" element={<AdminRoute><ContadorDetallePage /></AdminRoute>} />
          <Route path="/admin/liquidacion" element={<AdminRoute><LiquidacionPage /></AdminRoute>} />
          <Route path="/impuestos" element={<ProtectedRoute><CalculadoraImpuestosPage /></ProtectedRoute>} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return <AppRoutes />;
}

export default App;

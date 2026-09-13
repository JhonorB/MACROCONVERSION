import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import Dashboard from '../components/dashboard/Dashboard';
import { useProcesador } from '../hooks/useProcesador';

const HomePage = () => {
  const navigate = useNavigate();
  const { startProceso, loading } = useProcesador();

  const handleProcess = async (data) => {
    // In a real app, you would start process, get session ID and navigate
    // await startProceso(data);
    navigate('/proceso/demo-session');
  };

  return (
    <div className="min-h-screen bg-sire-dark">
      {loading && (
        <div className="fixed top-0 left-0 w-full h-1 bg-sire-secondary z-50">
          <div className="h-full bg-sire-blue animate-pulse w-full"></div>
        </div>
      )}
      <Dashboard onProcess={handleProcess} />
    </div>
  );
};

export default HomePage;

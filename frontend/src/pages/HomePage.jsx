import React from 'react';
import { useNavigate } from 'react-router-dom';
import Dashboard from '../components/dashboard/Dashboard';
import { useProcesador } from '../hooks/useProcesador';

const HomePage = () => {
  const navigate = useNavigate();
  const { startProceso, loading } = useProcesador();

  const handleProcess = async (data) => {
    try {
      const sesion = await startProceso(data);
      if (sesion && sesion.id) {
        navigate(`/proceso/${sesion.id}`);
      }
    } catch (err) {
      // El error ya es manejado y notificado en useProcesador (Toast y state)
    }
  };

  return (
    <div className="min-h-screen bg-sire-dark">
      {loading && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center">
          <div className="w-16 h-16 border-4 border-sire-secondary border-t-sire-blue rounded-full animate-spin"></div>
          <p className="mt-4 text-white font-medium text-lg">Procesando archivo CSV en el servidor...</p>
          <p className="text-gray-400 text-sm mt-1">Extrayendo comprobantes, validando detracciones y estructurando macro...</p>
        </div>
      )}
      <Dashboard onProcess={handleProcess} />
    </div>
  );
};

export default HomePage;

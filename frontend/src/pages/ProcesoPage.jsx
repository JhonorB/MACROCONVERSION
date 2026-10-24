import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProcesador } from '../hooks/useProcesador';
import DetraccionesModal from '../components/detracciones/DetraccionesModal';
import AsignadorCuentas from '../components/cuentas/AsignadorCuentas';
import ResumenFinanciero from '../components/resumen/ResumenFinanciero';

const ProcesoPage = () => {
  const { sesionId } = useParams();
  const navigate = useNavigate();
  const { 
    estado, loading, error, detracciones, facturas, resumen, periodo,
    cargarSesion, confirmarDetracciones, asignarCuenta, generarFinal, descargar, resetProceso
  } = useProcesador(sesionId);

  useEffect(() => {
    if (sesionId) {
      cargarSesion(sesionId);
    }
  }, [sesionId, cargarSesion]);

  const handleNewProcess = () => {
    resetProceso();
    navigate('/');
  };

  const counters = {
    total: facturas.length,
    assigned: facturas.filter(f => f.cuenta_asignada).length,
    facturas: facturas.filter(f => (f.serie || '').startsWith('F')).length,
    boletas: facturas.filter(f => (f.serie || '').startsWith('B')).length,
    ncnd: facturas.filter(f => (f.serie || '').startsWith('N')).length,
  };

  return (
    <div className="min-h-screen flex flex-col bg-sire-dark">
      {loading && (
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center">
          <div className="w-16 h-16 border-4 border-sire-secondary border-t-sire-blue rounded-full animate-spin"></div>
          <p className="mt-4 text-white font-medium text-lg">Procesando información del servidor...</p>
        </div>
      )}

      {error && !loading && estado === 'UPLOAD' && (
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-sire-card p-6 rounded-2xl border border-sire-red/50 text-center shadow-2xl">
            <h3 className="text-xl font-bold text-sire-red mb-2">Error en la sesión</h3>
            <p className="text-gray-300 text-sm mb-6">{error}</p>
            <button
              onClick={handleNewProcess}
              className="px-6 py-3 bg-sire-blue hover:bg-blue-600 text-white rounded-xl font-medium transition shadow-lg"
            >
              Volver al Dashboard
            </button>
          </div>
        </div>
      )}

      <main className="flex-1 relative">
        {estado === 'DETRACCIONES' && (
          <DetraccionesModal 
            detracciones={detracciones}
            onConfirm={confirmarDetracciones}
          />
        )}

        {(estado === 'ASIGNACION' || (estado === 'DETRACCIONES' && facturas.length > 0)) && (
          <AsignadorCuentas 
            facturas={facturas}
            counters={counters}
            periodo={periodo}
            onAssign={asignarCuenta}
            onGenerate={generarFinal}
          />
        )}

        {estado === 'COMPLETED' && (
          <ResumenFinanciero 
            resumen={resumen}
            onDownload={descargar}
            onNewProcess={handleNewProcess}
          />
        )}
      </main>
    </div>
  );
};

export default ProcesoPage;

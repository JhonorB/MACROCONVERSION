import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import { useProcesador } from '../hooks/useProcesador';
import DetraccionesModal from '../components/detracciones/DetraccionesModal';
import AsignadorCuentas from '../components/cuentas/AsignadorCuentas';
import ResumenFinanciero from '../components/resumen/ResumenFinanciero';

const ProcesoPage = () => {
  const { sesionId } = useParams();
  const navigate = useNavigate();
  const { 
    estado, loading, detracciones, facturas, resumen,
    startProceso, confirmarDetracciones, asignarCuenta, generarFinal, descargar, resetProceso
  } = useProcesador();

  // Mock initial load for demo
  useEffect(() => {
    if (estado === 'UPLOAD') {
      startProceso({ tipo: 'COM' });
    }
  }, []);

  const handleNewProcess = () => {
    resetProceso();
    navigate('/');
  };

  const counters = {
    total: facturas.length,
    assigned: facturas.filter(f => f.cuenta_asignada).length,
    facturas: facturas.filter(f => f.serie.startsWith('F')).length,
    boletas: facturas.filter(f => f.serie.startsWith('B')).length,
    ncnd: facturas.filter(f => f.serie.startsWith('N')).length,
  };

  return (
    <div className="min-h-screen flex flex-col bg-sire-dark">
      <Header />
      
      {loading && (
        <div className="absolute inset-0 z-[100] bg-black/50 backdrop-blur-sm flex flex-col items-center justify-center">
          <div className="w-16 h-16 border-4 border-sire-secondary border-t-sire-blue rounded-full animate-spin"></div>
          <p className="mt-4 text-white font-medium text-lg">Procesando información...</p>
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

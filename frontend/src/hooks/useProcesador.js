import { useState } from 'react';
import * as api from '../api/client';
import { showToast } from '../components/layout/Toast';

export const useProcesador = () => {
  const [sesionId, setSesionId] = useState(null);
  const [estado, setEstado] = useState('UPLOAD'); // UPLOAD, DETRACCIONES, ASIGNACION, COMPLETED
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [detracciones, setDetracciones] = useState([]);
  const [facturas, setFacturas] = useState([]);
  const [resumen, setResumen] = useState(null);

  const startProceso = async (data) => {
    try {
      setLoading(true);
      // const formData = new FormData();
      // formData.append('file', data.file);
      // ... append other fields
      // const res = await api.uploadCsv(formData);
      
      // Mocking flow
      setTimeout(() => {
        setSesionId('mock-session-123');
        if (data.tipo === 'COM') {
          setDetracciones([
            { serie: 'F001', numero: '001234', ruc: '20123456789', razon_social: 'PROVEEDOR A SAC', fecha: '15/07/2026', importe: 1500.00 }
          ]);
          setEstado('DETRACCIONES');
        } else {
          generarFinal('mock-session-123');
        }
        setLoading(false);
      }, 1500);
      
    } catch (err) {
      setError(err.message);
      setLoading(false);
      showToast.error('Error al procesar el archivo');
    }
  };

  const confirmarDetracciones = async (excludedIndices) => {
    try {
      setLoading(true);
      // await api.confirmarDetracciones(sesionId, excludedIndices);
      
      // Mock flow to Asignacion
      setTimeout(() => {
        setFacturas([
          { id: 1, serie: 'F001', numero: '001234', ruc: '20123456789', razon_social: 'PROVEEDOR A SAC', importe: 1500.00, cuenta_asignada: null },
          { id: 2, serie: 'F002', numero: '009988', ruc: '20987654321', razon_social: 'PROVEEDOR B SAC', importe: 450.50, cuenta_asignada: null }
        ]);
        setEstado('ASIGNACION');
        setLoading(false);
      }, 1000);
    } catch (err) {
      setLoading(false);
      showToast.error('Error al confirmar detracciones');
    }
  };

  const asignarCuenta = async (facturaId, cuentaCodigo, aplicarARuc) => {
    try {
      // api call
      setFacturas(prev => prev.map(f => {
        if (aplicarARuc) {
          const target = prev.find(pf => pf.id === facturaId);
          if (f.ruc === target.ruc) return { ...f, cuenta_asignada: cuentaCodigo };
        }
        if (f.id === facturaId) return { ...f, cuenta_asignada: cuentaCodigo };
        return f;
      }));
    } catch (err) {
      showToast.error('Error al asignar cuenta');
    }
  };

  const generarFinal = async (sid = sesionId) => {
    try {
      setLoading(true);
      // await api.generarExcel(sid);
      // const res = await api.getResumen(sid);
      
      setTimeout(() => {
        setResumen({
          empresa: 'EMPRESA DEMO SAC',
          periodo: 'JULIO 2026',
          base_imponible: '10,500.00',
          igv: '1,890.00',
          total: '12,390.00',
          tasas: '18%'
        });
        setEstado('COMPLETED');
        setLoading(false);
      }, 1500);
    } catch (err) {
      setLoading(false);
      showToast.error('Error al generar Excel');
    }
  };

  const descargar = async () => {
    showToast.success('Descargando archivo...');
    // const blob = await api.descargarExcel(sesionId);
    // trigger download logic
  };

  const resetProceso = () => {
    setSesionId(null);
    setEstado('UPLOAD');
    setDetracciones([]);
    setFacturas([]);
    setResumen(null);
    setError(null);
  };

  return {
    sesionId, estado, loading, error, detracciones, facturas, resumen,
    startProceso, confirmarDetracciones, asignarCuenta, generarFinal, descargar, resetProceso
  };
};

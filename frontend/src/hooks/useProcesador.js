import { useState, useCallback } from 'react';
import * as api from '../api/client';
import { showToast } from '../components/layout/Toast';

export const useProcesador = (initialSesionId = null) => {
  const [sesionId, setSesionId] = useState(initialSesionId);
  const [sesionData, setSesionData] = useState(null);
  const [estado, setEstado] = useState('UPLOAD'); // UPLOAD, DETRACCIONES, ASIGNACION, COMPLETED
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [detracciones, setDetracciones] = useState([]);
  const [facturas, setFacturas] = useState([]);
  const [resumen, setResumen] = useState(null);
  const [periodo, setPeriodo] = useState('');

  // Normalizador de facturas recibidas del backend
  const formatFactura = (f) => ({
    id: f.ID || f.id,
    serie: f.SERIE || f.serie || '',
    numero: f.NUMERO || f.numero || '',
    ruc: f.CODENT || f.ruc || '',
    razon_social: f.RAZSOC || f.razon_social || 'RAZON SOCIAL NO INFORMADA',
    importe: parseFloat(f.VALVTA || f.importe || 0),
    fecha: f.FECEMI || f.fecha || '',
    tipo_doc: f.TIPDOC || f.tipo_doc || '',
    tiene_detraccion: f.TIENE_D || false,
    cuenta_asignada: f.cuenta_asignada || null,
    idx_df: f.idx_df !== undefined ? f.idx_df : f.idx
  });

  // Normalizador de detracciones
  const formatDetraccion = (d, index) => {
    const parts = (d.serie_num || '').split('-');
    return {
      idx: d.idx !== undefined ? d.idx : index,
      serie: d.serie || parts[0] || '',
      numero: d.numero || parts[1] || '',
      fecha: d.fecemi || d.fecha || '',
      ruc: d.ruc || '',
      razon_social: d.razsoc || d.razon_social || d.texto || 'PROVEEDOR',
      importe: parseFloat(d.monto || d.importe || 0)
    };
  };

  // Cargar una sesión existente por su ID
  const cargarSesion = useCallback(async (sid) => {
    if (!sid) return;
    try {
      setLoading(true);
      setError(null);
      setSesionId(sid);
      
      const res = await api.getSesion(sid);
      const sesion = res.data;
      setSesionData(sesion);
      setEstado(sesion.estado);
      setPeriodo(`${sesion.mes}/${sesion.anio}`);

      if (sesion.estado === 'DETRACCIONES') {
        const detRes = await api.getDetracciones(sid);
        const rawDet = Array.isArray(detRes.data) ? detRes.data : (sesion.datos_detracciones || []);
        setDetracciones(rawDet.map(formatDetraccion));
      } else if (sesion.estado === 'ASIGNACION') {
        const facRes = await api.getFacturas(sid);
        const rawFac = Array.isArray(facRes.data) ? facRes.data : (sesion.datos_prescan?.facturas || []);
        setFacturas(rawFac.map(formatFactura));
      } else if (sesion.estado === 'COMPLETED') {
        if (sesion.resumen) {
          setResumen(sesion.resumen);
        } else {
          const resResumen = await api.getResumen(sid);
          setResumen(resResumen.data);
        }
      }
      return sesion;
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Error al cargar la sesión del proceso';
      setError(msg);
      showToast.error(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Iniciar proceso cargando el archivo CSV real
  const startProceso = async (data) => {
    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('csv_file', data.file);
      formData.append('empresa_id', data.empresaId);
      formData.append('tipo', data.tipo);
      if (data.subtipoVta) formData.append('subtipo_vta', data.subtipoVta);
      formData.append('anio', data.anio);
      formData.append('mes', data.mes);

      const res = await api.uploadCsv(formData);
      const sesion = res.data;

      setSesionId(sesion.id);
      setSesionData(sesion);
      setEstado(sesion.estado);
      setPeriodo(`${sesion.mes}/${sesion.anio}`);

      if (sesion.estado === 'DETRACCIONES') {
        const rawDet = sesion.datos_detracciones || [];
        setDetracciones(rawDet.map(formatDetraccion));
      } else if (sesion.estado === 'ASIGNACION') {
        const rawFac = sesion.datos_prescan?.facturas || [];
        setFacturas(rawFac.map(formatFactura));
      } else if (sesion.estado === 'COMPLETED') {
        setResumen(sesion.resumen);
      }

      showToast.success(`Archivo procesado. Sesión #${sesion.id} creada.`);
      return sesion;
    } catch (err) {
      let msg = 'Error al procesar el archivo CSV';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') msg = err.response.data;
        else if (err.response.data.error) msg = err.response.data.error;
        else if (err.response.data.csv_file) msg = `Archivo: ${err.response.data.csv_file.join(', ')}`;
        else if (err.response.data.mes) msg = `Mes: ${err.response.data.mes.join(', ')}`;
        else if (err.response.data.anio) msg = `Año: ${err.response.data.anio.join(', ')}`;
        else msg = JSON.stringify(err.response.data);
      }
      setError(msg);
      showToast.error(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  // Confirmar exclusiones de detracciones
  const confirmarDetracciones = async (excludedIndices) => {
    if (!sesionId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.confirmarDetracciones(sesionId, excludedIndices);
      const sesion = res.data;
      setSesionData(sesion);
      setEstado('ASIGNACION');

      // Cargar facturas actualizadas de la sesión
      const facRes = await api.getFacturas(sesionId);
      const rawFac = Array.isArray(facRes.data) ? facRes.data : (sesion.datos_prescan?.facturas || []);
      setFacturas(rawFac.map(formatFactura));

      showToast.success('Detracciones confirmadas correctamente.');
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al confirmar detracciones';
      setError(msg);
      showToast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // Asignar cuenta contable a una factura o masivamente por RUC
  const asignarCuenta = async (facturaId, cuentaCodigo, aplicarARuc = false) => {
    if (!sesionId) return;
    try {
      await api.asignarCuenta(sesionId, facturaId, cuentaCodigo, aplicarARuc);
      
      // Actualizar estado local inmediato
      setFacturas(prev => prev.map(f => {
        if (aplicarARuc) {
          const target = prev.find(pf => pf.id === facturaId);
          if (target && f.ruc === target.ruc) {
            return { ...f, cuenta_asignada: cuentaCodigo };
          }
        }
        if (f.id === facturaId) {
          return { ...f, cuenta_asignada: cuentaCodigo };
        }
        return f;
      }));

      showToast.success(`Cuenta ${cuentaCodigo} asignada.`);
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.cuenta_codigo?.[0] || 'Error al asignar cuenta contable';
      showToast.error(msg);
    }
  };

  // Generar archivo Excel final
  const generarFinal = async (sid = sesionId) => {
    const targetSid = sid || sesionId;
    if (!targetSid) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.generarExcel(targetSid);
      const sesion = res.data;
      setSesionData(sesion);
      setResumen(sesion.resumen);
      setEstado('COMPLETED');
      showToast.success('¡Macro Excel generada exitosamente!');
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al generar el archivo Excel';
      setError(msg);
      showToast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // Descargar archivo Excel generado
  const descargar = async () => {
    if (!sesionId) return;
    try {
      setLoading(true);
      showToast.info('Descargando archivo Excel...');
      const res = await api.descargarExcel(sesionId);
      
      let filename = `PROCESO_${sesionId}.xlsx`;
      if (sesionData?.tipo && sesionData?.empresa_detalle?.codigo) {
        filename = `${sesionData.tipo}${sesionData.empresa_detalle.codigo}${sesionData.anio}${sesionData.mes}.xlsx`;
      }
      
      const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      showToast.success('Descarga completada.');
    } catch (err) {
      showToast.error('Error al descargar el archivo Excel.');
    } finally {
      setLoading(false);
    }
  };

  const resetProceso = () => {
    setSesionId(null);
    setSesionData(null);
    setEstado('UPLOAD');
    setDetracciones([]);
    setFacturas([]);
    setResumen(null);
    setError(null);
    setPeriodo('');
  };

  return {
    sesionId, sesionData, estado, loading, error, detracciones, facturas, resumen, periodo,
    cargarSesion, startProceso, confirmarDetracciones, asignarCuenta, generarFinal, descargar, resetProceso
  };
};

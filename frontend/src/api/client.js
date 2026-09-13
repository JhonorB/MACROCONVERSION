import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Empresas
export const getEmpresas = (query = '') => client.get(`/empresas/${query ? `?q=${query}` : ''}`);
export const createEmpresa = (data) => client.post('/empresas/', data);
export const updateEmpresa = (id, data) => client.patch(`/empresas/${id}/`, data);
export const deleteEmpresa = (id) => client.delete(`/empresas/${id}/`);

// Cuentas
export const getCuentas = (query = '') => client.get(`/cuentas/${query ? `?q=${query}` : ''}`);
export const getCuentasSugeridas = (ruc) => client.get(`/cuentas/sugeridas/${ruc}/`);

// Proceso
export const uploadCsv = (formData) => client.post('/procesos/upload_csv/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
export const getDetracciones = (sesionId) => client.get(`/procesos/${sesionId}/detracciones/`);
export const confirmarDetracciones = (sesionId, excluidos) => client.post(`/procesos/${sesionId}/detracciones/`, { excluidos });

export const getFacturas = (sesionId) => client.get(`/procesos/${sesionId}/facturas/`);
export const asignarCuenta = (sesionId, facturaId, cuentaCodigo, aplicarARuc = false) =>
  client.post(`/procesos/${sesionId}/asignar_cuenta/`, { factura_id: facturaId, cuenta_codigo: cuentaCodigo, aplicar_a_ruc: aplicarARuc });
export const asignarCuentaMasivo = (sesionId, ruc, cuentaCodigo) =>
  client.post(`/procesos/${sesionId}/asignar_cuenta/`, { factura_id: `bulk-${ruc}`, cuenta_codigo: cuentaCodigo, aplicar_a_ruc: true });

export const generarExcel = (sesionId) => client.post(`/procesos/${sesionId}/generar/`);
export const descargarExcel = (sesionId) => client.get(`/procesos/${sesionId}/descargar/`, { responseType: 'blob' });

export const getResumen = (sesionId) => client.get(`/procesos/${sesionId}/resumen/`);

// Comprobantes
export const buscarComprobante = (serie, numero, ruc) => client.post('/comprobantes/buscar/', { serie, numero, ruc });
export const uploadComprobantes = (formData) => client.post('/comprobantes/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
export const verComprobante = (filename) => `${client.defaults.baseURL}/comprobantes/ver/?filename=${filename}`;

// Auth
export const loginUser = (username, password) => client.post('/auth/login/', { username, password });
export const logoutUser = () => client.post('/auth/logout/');
export const checkAuth = () => client.get('/auth/check/');

// Dashboard
export const getDashboardStats = () => client.get('/dashboard/stats/');

// Contadores Management (Admin only)
export const getContadores = () => client.get('/contadores/');
export const createContador = (data) => client.post('/contadores/', data);
export const updateContador = (id, data) => client.patch(`/contadores/${id}/`, data);
export const deleteContador = (id) => client.delete(`/contadores/${id}/`);
export const activarContador = (id) => client.post(`/contadores/${id}/toggle-estado/`);
export const getContadorDetalle = (id) => client.get(`/contadores/${id}/detalle/`);

// Liquidacion (Admin only)
export const getLiquidacion = (mes, anio) => client.get('/liquidacion/', { params: { mes, anio } });

// Impuestos
export const getCalculadoraImpuestos = (empresa, anio, mes) => client.get('/impuestos/calcular/', { params: { empresa, anio, mes } });
export const saveLiquidacionImpuesto = (data) => client.post('/impuestos/calcular/', data);

export default client;

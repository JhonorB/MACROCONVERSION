import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  DocumentTextIcon, 
  ShoppingCartIcon, 
  BuildingOfficeIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';
import { getLiquidacion } from '../api/client';

const LiquidacionPage = () => {
  const currentDate = new Date();
  const currentMonth = String(currentDate.getMonth() + 1).padStart(2, '0');
  const currentYear = String(currentDate.getFullYear()).slice(-2); // 2-digit year

  const [mes, setMes] = useState(currentMonth);
  const [anio, setAnio] = useState(currentYear);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const meses = [
    { value: '01', label: 'Enero' },
    { value: '02', label: 'Febrero' },
    { value: '03', label: 'Marzo' },
    { value: '04', label: 'Abril' },
    { value: '05', label: 'Mayo' },
    { value: '06', label: 'Junio' },
    { value: '07', label: 'Julio' },
    { value: '08', label: 'Agosto' },
    { value: '09', label: 'Septiembre' },
    { value: '10', label: 'Octubre' },
    { value: '11', label: 'Noviembre' },
    { value: '12', label: 'Diciembre' },
  ];

  const años = ['23', '24', '25', '26', '27', '28', '29', '30'];

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getLiquidacion(mes, anio);
      setData(response.data || []);
    } catch (err) {
      console.error('Error fetching liquidacion:', err);
      setError('Ocurrió un error al obtener la liquidación.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, anio]);

  // Calculate totals
  const totalCompras = data.reduce((acc, curr) => acc + (Number(curr.total_compras) || 0), 0);
  const totalVentas = data.reduce((acc, curr) => acc + (Number(curr.total_ventas) || 0), 0);
  const totalEmpresas = data.reduce((acc, curr) => acc + (Number(curr.total_empresas) || 0), 0);

  return (
    <div className="min-h-screen bg-sire-dark text-white p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-sire-blue to-sire-green bg-clip-text text-transparent flex items-center">
              🧾 Liquidación Mensual
            </h1>
            <p className="text-gray-400 mt-2">
              Resumen de operaciones por contador para el periodo seleccionado.
            </p>
          </div>
          
          <div className="flex bg-sire-card p-2 rounded-2xl border border-sire-secondary gap-3 items-center shadow-lg">
            <CalendarDaysIcon className="w-6 h-6 text-sire-blue ml-2" />
            <select
              value={mes}
              onChange={(e) => setMes(e.target.value)}
              className="bg-sire-dark border border-sire-secondary rounded-xl px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-sire-blue transition-all"
            >
              {meses.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
            <span className="text-gray-500 font-bold">/</span>
            <select
              value={anio}
              onChange={(e) => setAnio(e.target.value)}
              className="bg-sire-dark border border-sire-secondary rounded-xl px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-sire-blue transition-all"
            >
              {años.map(a => (
                <option key={a} value={a}>20{a}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-sire-card rounded-3xl p-6 border border-sire-secondary shadow-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <ShoppingCartIcon className="w-24 h-24 text-sire-blue" />
            </div>
            <h3 className="text-gray-400 font-medium mb-1">Total Compras</h3>
            <p className="text-4xl font-bold text-white">{totalCompras}</p>
            <div className="mt-4 h-1 w-full bg-sire-secondary rounded-full overflow-hidden">
              <div className="h-full bg-sire-blue w-1/2 rounded-full"></div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-sire-card rounded-3xl p-6 border border-sire-secondary shadow-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <DocumentTextIcon className="w-24 h-24 text-sire-green" />
            </div>
            <h3 className="text-gray-400 font-medium mb-1">Total Ventas</h3>
            <p className="text-4xl font-bold text-white">{totalVentas}</p>
            <div className="mt-4 h-1 w-full bg-sire-secondary rounded-full overflow-hidden">
              <div className="h-full bg-sire-green w-1/2 rounded-full"></div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-sire-card rounded-3xl p-6 border border-sire-secondary shadow-xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <BuildingOfficeIcon className="w-24 h-24 text-purple-500" />
            </div>
            <h3 className="text-gray-400 font-medium mb-1">Empresas Únicas</h3>
            <p className="text-4xl font-bold text-white">{totalEmpresas}</p>
            <div className="mt-4 h-1 w-full bg-sire-secondary rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 w-1/2 rounded-full"></div>
            </div>
          </motion.div>
        </div>

        {/* Details Table */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-sire-card rounded-3xl border border-sire-secondary shadow-xl overflow-hidden"
        >
          <div className="p-6 border-b border-sire-secondary bg-sire-dark/30">
            <h2 className="text-xl font-bold text-white">Detalle por Contador</h2>
          </div>
          
          <div className="overflow-x-auto">
            {loading ? (
              <div className="p-12 flex justify-center items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div>
              </div>
            ) : error ? (
              <div className="p-12 text-center text-red-400 bg-red-400/10">
                {error}
              </div>
            ) : data.length === 0 ? (
              <div className="p-12 text-center text-gray-400">
                No hay datos disponibles para el periodo {mes}/20{anio}.
              </div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-sire-dark/50 text-gray-400 text-sm uppercase tracking-wider">
                    <th className="px-6 py-4 font-medium">Contador</th>
                    <th className="px-6 py-4 font-medium text-center">Compras</th>
                    <th className="px-6 py-4 font-medium text-center">Ventas</th>
                    <th className="px-6 py-4 font-medium text-center">Empresas Únicas</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sire-secondary">
                  {data.map((item, index) => (
                    <motion.tr 
                      key={item.id || index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * index }}
                      className="hover:bg-sire-dark/40 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-sire-blue to-purple-600 flex items-center justify-center text-white font-bold shadow-md">
                            {(item.nombre || item.username || '?').charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="font-bold text-white">{item.nombre || item.username}</p>
                            {item.nombre && item.username && (
                              <p className="text-xs text-gray-400">@{item.username}</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-sire-blue/10 text-sire-blue border border-sire-blue/20">
                          {item.total_compras || 0}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-sire-green/10 text-sire-green border border-sire-green/20">
                          {item.total_ventas || 0}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                          {item.total_empresas || 0}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LiquidacionPage;

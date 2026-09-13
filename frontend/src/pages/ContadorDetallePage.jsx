import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeftIcon, 
  BuildingOfficeIcon, 
  DocumentDuplicateIcon,
  CheckBadgeIcon
} from '@heroicons/react/24/outline';
import * as api from '../api/client';
import toast from 'react-hot-toast';

const ContadorDetallePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contador, setContador] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('empresas');

  useEffect(() => {
    const fetchDetalle = async () => {
      try {
        setLoading(true);
        const res = await api.getContadorDetalle(id);
        setContador(res.data);
      } catch (error) {
        toast.error('Error al cargar detalles del contador');
        navigate('/admin/contadores');
      } finally {
        setLoading(false);
      }
    };
    fetchDetalle();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div>
      </div>
    );
  }

  if (!contador) return null;

  const { detalle } = contador;
  const empresas = detalle?.empresas || [];
  const procesos = detalle?.ultimos_procesos || [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <button 
        onClick={() => navigate('/admin/contadores')}
        className="flex items-center text-gray-400 hover:text-white transition-colors mb-6 font-medium"
      >
        <ArrowLeftIcon className="w-4 h-4 mr-2" />
        Volver a Contadores
      </button>

      {/* Header Profile */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-sire-card border border-sire-secondary rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center md:items-start gap-6 shadow-xl mb-8 relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-sire-blue/20 to-purple-600/20 opacity-50 z-0"></div>
        
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-sire-blue to-purple-600 flex items-center justify-center text-white font-bold text-4xl shadow-lg border-4 border-sire-card z-10">
          {contador.first_name ? contador.first_name.charAt(0).toUpperCase() : contador.username.charAt(0).toUpperCase()}
        </div>
        
        <div className="flex-grow text-center md:text-left z-10">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">
                {contador.first_name} {contador.last_name}
              </h1>
              <p className="text-lg text-sire-blue font-medium mb-3">@{contador.username}</p>
              
              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-gray-300">
                <span className="flex items-center">
                  <span className="text-gray-500 mr-2">Email:</span> {contador.email || '-'}
                </span>
                <span className="flex items-center">
                  <span className="text-gray-500 mr-2">Teléfono:</span> {contador.telefono || '-'}
                </span>
                <span className="flex items-center">
                  <span className="text-gray-500 mr-2">Registro:</span> {new Date(contador.date_joined).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className={`px-4 py-1.5 text-sm font-bold rounded-full border ${
                contador.estado === 'ACTIVO' ? 'bg-sire-green/20 text-sire-green border-sire-green/30' : 'bg-red-500/20 text-red-400 border-red-500/30'
              }`}>
                {contador.estado === 'ACTIVO' ? '🟢 ACTIVO' : '🔴 INACTIVO'}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex border-b border-sire-secondary mb-6">
        <button
          onClick={() => setActiveTab('empresas')}
          className={`px-6 py-3 font-medium text-sm transition-colors border-b-2 ${
            activeTab === 'empresas' ? 'border-sire-blue text-sire-blue' : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          🏢 Empresas ({empresas.length})
        </button>
        <button
          onClick={() => setActiveTab('procesos')}
          className={`px-6 py-3 font-medium text-sm transition-colors border-b-2 ${
            activeTab === 'procesos' ? 'border-sire-blue text-sire-blue' : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          📋 Últimos Procesos
        </button>
        <button
          onClick={() => setActiveTab('estadisticas')}
          className={`px-6 py-3 font-medium text-sm transition-colors border-b-2 ${
            activeTab === 'estadisticas' ? 'border-sire-blue text-sire-blue' : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          📊 Estadísticas
        </button>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'empresas' && (
          <div className="bg-sire-card border border-sire-secondary rounded-xl overflow-hidden">
            {empresas.length > 0 ? (
              <table className="w-full text-left">
                <thead className="bg-sire-dark/50 text-gray-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4 font-medium">RUC</th>
                    <th className="px-6 py-4 font-medium">Razón Social</th>
                    <th className="px-6 py-4 font-medium">Procesos Realizados</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sire-secondary/50">
                  {empresas.map((emp) => (
                    <tr key={emp.id} className="hover:bg-sire-dark/30 transition-colors">
                      <td className="px-6 py-4 text-white font-medium">{emp.ruc}</td>
                      <td className="px-6 py-4 text-gray-300">{emp.razon_social}</td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-sire-blue/10 text-sire-blue rounded-lg text-xs font-bold">
                          {emp.procesos_count || 0}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-400">
                <BuildingOfficeIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Este contador aún no tiene empresas registradas.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'procesos' && (
          <div className="bg-sire-card border border-sire-secondary rounded-xl overflow-hidden">
            {procesos.length > 0 ? (
              <table className="w-full text-left">
                <thead className="bg-sire-dark/50 text-gray-400 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4 font-medium">Tipo</th>
                    <th className="px-6 py-4 font-medium">Empresa (RUC)</th>
                    <th className="px-6 py-4 font-medium">Periodo</th>
                    <th className="px-6 py-4 font-medium">Fecha</th>
                    <th className="px-6 py-4 font-medium">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sire-secondary/50">
                  {procesos.map((proc) => (
                    <tr key={proc.id} className="hover:bg-sire-dark/30 transition-colors">
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-bold rounded ${
                          proc.tipo === 'COM' ? 'bg-sire-blue/20 text-sire-blue' : 'bg-sire-green/20 text-sire-green'
                        }`}>
                          {proc.tipo}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-300 text-sm">
                        {proc.empresa__ruc}
                      </td>
                      <td className="px-6 py-4 text-gray-300 text-sm">
                        {proc.periodo}
                      </td>
                      <td className="px-6 py-4 text-gray-400 text-sm">
                        {new Date(proc.fecha_creacion).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${
                          proc.estado === 'COMPLETADO' ? 'bg-emerald-500/10 text-emerald-400' :
                          proc.estado === 'PENDIENTE' ? 'bg-amber-500/10 text-amber-400' :
                          'bg-red-500/10 text-red-400'
                        }`}>
                          {proc.estado === 'COMPLETADO' && <CheckBadgeIcon className="w-3.5 h-3.5 mr-1" />}
                          {proc.estado}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-400">
                <DocumentDuplicateIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No se encontraron procesos recientes.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'estadisticas' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 font-medium text-sm">Total Empresas</h3>
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <BuildingOfficeIcon className="w-5 h-5 text-blue-400" />
                </div>
              </div>
              <p className="text-4xl font-bold text-white">{empresas.length}</p>
            </div>
            
            <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 font-medium text-sm">Total Procesos (COM + VTA)</h3>
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <DocumentDuplicateIcon className="w-5 h-5 text-emerald-400" />
                </div>
              </div>
              <p className="text-4xl font-bold text-white">{contador.procesos_count || 0}</p>
            </div>

            <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 shadow-lg flex flex-col justify-center">
              <p className="text-gray-400 text-sm mb-2">Estado de la cuenta</p>
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 animate-pulse ${contador.estado === 'ACTIVO' ? 'bg-sire-green' : 'bg-red-500'}`}></div>
                <span className={`text-lg font-bold ${contador.estado === 'ACTIVO' ? 'text-sire-green' : 'text-red-400'}`}>
                  {contador.estado === 'ACTIVO' ? 'Operativo' : 'Desactivado'}
                </span>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ContadorDetallePage;

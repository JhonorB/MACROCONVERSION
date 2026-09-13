import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import * as api from '../../api/client';
import { BuildingOfficeIcon, DocumentDuplicateIcon, CheckBadgeIcon, ClockIcon, PlusIcon, CogIcon, UserGroupIcon } from '@heroicons/react/24/outline';

const StatsBoard = () => {
  const navigate = useNavigate();
  const { rol } = useAuth();
  const isAdmin = rol === 'ADMIN';
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.getDashboardStats();
        setDashboardData(res.data);
      } catch (err) {
        console.error('Error fetching dashboard stats', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const stats = [
    { title: 'Total Empresas', value: dashboardData?.total_empresas || 0, icon: BuildingOfficeIcon, color: 'text-blue-400', bg: 'from-blue-500/10 to-transparent', border: 'border-blue-500/20' },
    { title: 'Total Procesos', value: dashboardData?.total_procesos || 0, icon: DocumentDuplicateIcon, color: 'text-sire-green', bg: 'from-sire-green/10 to-transparent', border: 'border-sire-green/20' },
    { title: 'Completados', value: dashboardData?.procesos_completados || 0, icon: CheckBadgeIcon, color: 'text-emerald-400', bg: 'from-emerald-500/10 to-transparent', border: 'border-emerald-500/20' },
    { title: 'Pendientes', value: dashboardData?.procesos_pendientes || 0, icon: ClockIcon, color: 'text-amber-400', bg: 'from-amber-500/10 to-transparent', border: 'border-amber-500/20' },
  ];

  if (isAdmin) {
    stats.push({ title: 'Total Contadores', value: dashboardData?.total_contadores || 0, icon: UserGroupIcon, color: 'text-purple-400', bg: 'from-purple-500/10 to-transparent', border: 'border-purple-500/20' });
  }

  const topEmpresas = dashboardData?.top_empresas?.map((e, idx) => ({
    id: e.codigo, rank: idx + 1, name: e.razon_social, ruc: e.ruc, count: e.num_procesos
  })) || [];

  const recentActivity = dashboardData?.procesos_recientes?.map((p) => ({
    id: p.id, empresa: p.empresa, tipo: p.tipo, periodo: p.periodo, estado: p.estado, fecha: new Date(p.created_at).toLocaleString()
  })) || [];

  const totalProcesosType = (dashboardData?.compras_count || 0) + (dashboardData?.ventas_count || 0);
  const comprasPerc = totalProcesosType > 0 ? Math.round(((dashboardData?.compras_count || 0) / totalProcesosType) * 100) : 0;
  const ventasPerc = totalProcesosType > 0 ? Math.round(((dashboardData?.ventas_count || 0) / totalProcesosType) * 100) : 0;
  const totalCuentas = dashboardData?.total_cuentas || 0;

  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1 } } };
  const itemVariants = { hidden: { y: 20, opacity: 0 }, visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 100 } } };

  if (loading) return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div></div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col md-flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Panel de Control</h1>
          <p className="text-gray-400 text-sm">Resumen de actividad y estadisticas del sistema</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {isAdmin && (
            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => navigate('/admin/contadores')} className="flex items-center px-4 py-2 bg-sire-dark border border-purple-500 text-purple-400 rounded-lg font-medium hover:bg-purple-500/10 transition-colors">
              <UserGroupIcon className="w-5 h-5 mr-2" /> Gestionar Contadores
            </motion.button>
          )}
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => navigate('/proceso')} className="flex items-center px-4 py-2 bg-sire-green text-white rounded-lg font-medium hover:bg-emerald-500 shadow-lg shadow-sire-green/20 transition-colors">
            <PlusIcon className="w-5 h-5 mr-2" /> Nuevo Proceso
          </motion.button>
        </div>
      </div>

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, idx) => (
            <motion.div key={idx} variants={itemVariants} whileHover={{ y: -5, scale: 1.02 }} className={`relative overflow-hidden bg-sire-card rounded-xl p-6 border ${stat.border} shadow-lg`}>
              <div className={`absolute inset-0 bg-gradient-to-r ${stat.bg} opacity-50`}></div>
              <div className="relative z-10 flex justify-between items-start">
                <div>
                  <p className="text-gray-400 text-sm font-medium mb-1">{stat.title}</p>
                  <motion.h3 initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.5 }} className="text-3xl font-bold text-white">{stat.value}</motion.h3>
                </div>
                <div className={`p-2 rounded-lg bg-sire-dark ${stat.border} border`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <motion.div variants={itemVariants} className="lg:col-span-3 bg-sire-card rounded-xl border border-sire-secondary shadow-lg overflow-hidden flex flex-col">
            <div className="p-6 border-b border-sire-secondary">
              <h2 className="text-lg font-bold text-white">Resumen de Actividad</h2>
            </div>
            <div className="p-6 flex-grow flex flex-col justify-center space-y-8">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-300 font-medium">Compras procesadas (COM)</span>
                  <span className="text-sire-blue font-bold">{comprasPerc}%</span>
                </div>
                <div className="w-full bg-sire-dark rounded-full h-3 border border-sire-secondary overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${comprasPerc}%` }} transition={{ duration: 1, delay: 0.5 }} className="bg-sire-blue h-full rounded-full"></motion.div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-300 font-medium">Ventas procesadas (VTA)</span>
                  <span className="text-sire-green font-bold">{ventasPerc}%</span>
                </div>
                <div className="w-full bg-sire-dark rounded-full h-3 border border-sire-secondary overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${ventasPerc}%` }} transition={{ duration: 1, delay: 0.7 }} className="bg-sire-green h-full rounded-full"></motion.div>
                </div>
              </div>
              <div className="pt-4 border-t border-sire-secondary/50 flex/items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Cuentas Contables Registradas</p>
                  <p className="text-2xl font-bold text-white mt-1">{totalCuentas}</p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="lg:col-span-2 bg-sire-card rounded-xl border border-sire-secondary shadow-lg overflow-hidden">
            <div className="p-6 border-b border-sire-secondary bg-sire-dark/30">
              <h2 className="text-lg font-bold text-white">Top Empresas</h2>
            </div>
            <div className="p-0">
              {topEmpresas.length === 0 ? (
                <div className="p-6 text-center text-gray-400 text-sm">No hay suficientes datos.</div>
              ) : topEmpresas.map((emp, idx) => (
                <div key={emp.id} className={`flex items-center p-4 border-b border-sire-secondary/50 hover:bg-sire-dark/50 transition-colors ${idx % 2 === 0 ? 'bg-sire-card' : 'bg-[#1e222d]'}`}>
                  <div className={`w-8 h-8 rounded-full flex/items-center justify-center font-bold text-sm mr-4 ${idx === 0 ? 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30' : idx === 1 ? 'bg-gray-300/20 text-gray-300 border border-gray-300/30' : idx === 2 ? 'bg-amber-600/20 text-amber-600 border border-amber-600/30' : 'bg-sire-dark text-gray-500 border border-sire-secondary'}`}>
                    {emp.rank}
                  </div>
                  <div className="flex-grow min-w-0">
                    <p className="text-sm font-bold text-white truncate">{emp.name}</p>
                    <p className="text-xs text-gray-400 truncate">RUC: {emp.ruc}</p>
                  </div>
                  <div className="ml-4"><span className="px-2.5 py-1 bg-sire-blue/10 text-sire-blue text-xs font-bold rounded-lg border border-sire-blue/20">{emp.count} proc.</span></div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <motion.div variants={itemVariants} className="bg-sire-card rounded-xl border border-sire-secondary shadow-lg overflow-hidden">
          <div className="p-6 border-b border-sire-secondary flex justify-between items-center">
            <h2 className="text-lg font-bold text-white">Actividad Reciente</h2>
          </div>
          <div className="overflow-x-auto">
            {recentActivity.length === 0 ? (
                <div className="p-6 text-center text-gray-400 text-sm">No hay actividad reciente.</div>
            ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-sire-dark/50 text-gray-400 text-xs uppercase tracking-wider">
                  <th className="p-4 font-medium">Empresa</th>
                  <th className="p-4 font-medium">Tipo</th>
                  <th className="p-4 font-medium">Periodo</th>
                  <th className="p-4 font-medium">Fecha</th>
                  <th className="p-4 font-medium text-right">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sire-secondary/50">
                {recentActivity.map((act) => (
                  <tr key={act.id} className="hover:bg-sire-dark/30 transition-colors">
                    <td className="p-4"><p className="text-sm font-medium text-white">{act.empresa}</p></td>
                    <td className="p-4"><span className={`px-2 py-1 text-xs font-bold rounded ${act.tipo === 'COM' ? 'bg-sire-blue/20 text-sire-blue' : 'bg-sire-green/20 text-sire-green'}`}>{act.tipo}</span></td>
                    <td className="p-4 text-sm text-gray-300">{act.periodo}</td>
                    <td className="p-4 text-sm text-gray-400">{act.fecha}</td>
                    <td className="p-4 text-right">
                      <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${act.estado === 'COMPLETADO' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : act.estado === 'PENDIENTE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                        {act.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            )}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};
export default StatsBoard;

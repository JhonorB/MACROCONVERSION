import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircleIcon, ArrowDownTrayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const ResumenFinanciero = ({ resumen, onDownload, onNewProcess }) => {
  const tasa = resumen?.tasa_detectada || resumen?.tasas || '18 %';
  const baseImponible = typeof resumen?.base_imponible === 'number' ? resumen.base_imponible.toLocaleString('es-PE', { minimumFractionDigits: 2 }) : (resumen?.base_imponible || '0.00');
  const igv = typeof resumen?.igv === 'number' ? resumen.igv.toLocaleString('es-PE', { minimumFractionDigits: 2 }) : (resumen?.igv || '0.00');
  const total = typeof resumen?.total === 'number' ? resumen.total.toLocaleString('es-PE', { minimumFractionDigits: 2 }) : (resumen?.total || '0.00');

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-4xl bg-sire-card rounded-2xl shadow-2xl border border-sire-secondary overflow-hidden"
      >
        {/* Header */}
        <div className="bg-sire-green/10 p-8 flex flex-col items-center text-center border-b border-sire-secondary relative overflow-hidden">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', bounce: 0.5 }}
          >
            <CheckCircleIcon className="w-20 h-20 text-sire-green mb-4" />
          </motion.div>
          <h2 className="text-3xl font-bold text-white mb-2">✓ Macro Excel Generada Exitosamente</h2>
          <p className="text-gray-400 text-lg">
            Empresa: <span className="text-white font-medium">{resumen?.empresa || 'Empresa seleccionada'}</span> | 
            Período: <span className="text-white font-medium">{resumen?.periodo || 'Período procesado'}</span>
          </p>
        </div>

        {/* Stats Grid */}
        <div className="p-8">
          <h3 className="text-xl font-bold text-white mb-6">Resumen Financiero del Período</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <motion.div whileHover={{ y: -5 }} className="bg-sire-dark p-6 rounded-xl border border-sire-secondary">
              <p className="text-sm text-gray-400 uppercase tracking-wider mb-2">Base Imponible</p>
              <p className="text-2xl font-bold text-white">S/ {baseImponible}</p>
            </motion.div>
            
            <motion.div whileHover={{ y: -5 }} className="bg-sire-dark p-6 rounded-xl border border-sire-secondary">
              <p className="text-sm text-gray-400 uppercase tracking-wider mb-2">IGV / IPM</p>
              <p className="text-2xl font-bold text-white">S/ {igv}</p>
            </motion.div>

            <motion.div whileHover={{ y: -5 }} className="bg-sire-dark p-6 rounded-xl border border-sire-blue/50 bg-sire-blue/5 shadow-[0_0_15px_rgba(24,119,242,0.1)]">
              <p className="text-sm text-sire-blue uppercase tracking-wider mb-2 font-semibold">Total General</p>
              <p className="text-4xl font-bold text-sire-blue">S/ {total}</p>
            </motion.div>

            <motion.div whileHover={{ y: -5 }} className="bg-sire-dark p-6 rounded-xl border border-sire-secondary">
              <p className="text-sm text-gray-400 uppercase tracking-wider mb-2">Tasas Detectadas</p>
              <p className="text-2xl font-bold text-white">{tasa}</p>
            </motion.div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button 
              onClick={onDownload}
              className="flex-1 flex items-center justify-center py-4 bg-sire-blue hover:bg-blue-600 text-white rounded-xl font-bold text-lg transition shadow-lg shadow-blue-500/20 cursor-pointer"
            >
              <ArrowDownTrayIcon className="w-6 h-6 mr-2" />
              📥 Descargar Excel
            </button>
            <button 
              onClick={onNewProcess}
              className="flex-1 flex items-center justify-center py-4 bg-transparent hover:bg-sire-secondary border border-sire-secondary text-white rounded-xl font-bold text-lg transition cursor-pointer"
            >
              <ArrowPathIcon className="w-6 h-6 mr-2" />
              🔄 Nuevo Proceso
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ResumenFinanciero;

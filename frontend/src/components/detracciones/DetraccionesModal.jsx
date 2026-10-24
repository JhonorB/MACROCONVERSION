import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExclamationTriangleIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';

const DetraccionesModal = ({ detracciones, onConfirm }) => {
  const [excluded, setExcluded] = useState(new Set());

  const toggleExclude = (id) => {
    setExcluded(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      >
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-sire-card w-full max-w-4xl rounded-2xl shadow-2xl border border-sire-secondary flex flex-col max-h-[90vh]"
        >
          {/* Header */}
          <div className="p-6 border-b border-sire-secondary flex items-center bg-sire-red/5 rounded-t-2xl">
            <ExclamationTriangleIcon className="w-8 h-8 text-sire-red mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-white">⚠️ ¡Detracciones Detectadas!</h2>
              <p className="text-gray-400 text-sm mt-1">Se encontraron {detracciones.length} comprobantes sujetos a detracción.</p>
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {detracciones.map((det, index) => {
              const detId = det.idx !== undefined ? det.idx : index;
              const isExcluded = excluded.has(detId);
              return (
                <div 
                  key={detId} 
                  className={`flex items-center justify-between p-4 rounded-xl border transition-colors ${
                    isExcluded ? 'border-sire-red/50 bg-sire-red/5 opacity-75' : 'border-sire-green/50 bg-sire-green/5'
                  }`}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      <span className="font-bold text-lg text-white">{det.serie}-{det.numero}</span>
                      <span className="text-sm bg-sire-dark px-2 py-1 rounded text-gray-300">{det.fecha}</span>
                      <button onClick={() => handleCopy(`${det.serie}-${det.numero}`)} className="text-gray-400 hover:text-white transition">
                        <DocumentDuplicateIcon className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-sm text-gray-400">{det.ruc} - <span className="text-gray-300">{det.razon_social}</span></p>
                  </div>
                  
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Importe</p>
                      <p className="font-bold text-white">S/ {Number(det.importe || 0).toFixed(2)}</p>
                    </div>
                    
                    {/* Toggle */}
                    <button 
                      onClick={() => toggleExclude(detId)}
                      className={`relative inline-flex h-8 w-16 items-center rounded-full transition-colors ${
                        isExcluded ? 'bg-sire-red' : 'bg-sire-green'
                      }`}
                    >
                      <span 
                        className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                          isExcluded ? 'translate-x-1' : 'translate-x-9'
                        }`} 
                      />
                    </button>
                    <span className={`w-20 text-xs font-bold text-center ${isExcluded ? 'text-sire-red' : 'text-sire-green'}`}>
                      {isExcluded ? 'EXCLUIDO' : 'PASAR'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-sire-secondary bg-sire-dark/50 rounded-b-2xl">
            <button 
              onClick={() => onConfirm(Array.from(excluded))}
              className="w-full py-4 bg-sire-green hover:bg-emerald-500 text-white rounded-xl font-bold text-lg transition shadow-lg"
            >
              Aceptar y Continuar
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DetraccionesModal;

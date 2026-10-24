import React from 'react';
import { motion } from 'framer-motion';
import { DocumentTextIcon, EyeIcon } from '@heroicons/react/24/outline';

const FacturaCard = ({ factura, isSelected, isAssigned, onSelect, onViewPdf }) => {
  const razonSocial = factura.razon_social || 'RAZON SOCIAL NO INFORMADA';
  const importeVal = Number(factura.importe || 0).toFixed(2);

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      onClick={onSelect}
      className={`relative p-4 rounded-xl cursor-pointer border transition-all duration-200 ${
        isSelected 
          ? 'border-sire-blue bg-sire-blue/10 shadow-[0_0_15px_rgba(24,119,242,0.2)]' 
          : isAssigned 
            ? 'border-sire-green/30 bg-sire-card hover:border-sire-green/60' 
            : 'border-sire-secondary bg-sire-card hover:border-gray-500'
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center space-x-2">
          <DocumentTextIcon className={`w-5 h-5 ${isAssigned ? 'text-sire-green' : 'text-gray-400'}`} />
          <span className="font-bold text-white">{factura.serie || 'S/S'}-{factura.numero || 'S/N'}</span>
        </div>
        <span className="font-bold text-gray-200">S/ {importeVal}</span>
      </div>
      
      <div className="mb-2">
        <p className="text-sm text-gray-400 truncate" title={`${factura.ruc || ''} - ${razonSocial}`}>
          <span className="text-gray-300 font-medium">{factura.ruc || 'S/RUC'}</span> - {razonSocial.substring(0, 34)}{razonSocial.length > 34 ? '...' : ''}
        </p>
      </div>
      
      <div className="flex justify-between items-center mt-3">
        <div className="flex-1">
          {isAssigned ? (
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-sire-green/20 text-sire-green border border-sire-green/30">
              ✓ Cuenta: {factura.cuenta_asignada}
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-500/20 text-orange-400 border border-orange-500/30">
              ⚠️ SIN CUENTA ASIGNADA
            </span>
          )}
        </div>
        
        {/* Actions */}
        <div className="flex space-x-2" style={{ opacity: isSelected ? 1 : 0.6 }}>
          {onViewPdf && (
            <button onClick={(e) => { e.stopPropagation(); onViewPdf(); }} className="p-1 text-gray-400 hover:text-sire-blue" title="Ver PDF">
              <EyeIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default FacturaCard;

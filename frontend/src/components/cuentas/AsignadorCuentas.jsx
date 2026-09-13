import React, { useState } from 'react';
import FacturaCard from './FacturaCard';
import CuentasList from './CuentasList';
import BuscadorCuentas from './BuscadorCuentas';

const AsignadorCuentas = ({ facturas, onAssign, onGenerate, counters, periodo }) => {
  const [selectedFacturaId, setSelectedFacturaId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [applyToAll, setApplyToAll] = useState(false);

  const selectedFactura = facturas.find(f => f.id === selectedFacturaId) || facturas.find(f => !f.cuenta_asignada) || facturas[0];
  const progress = Math.round((counters.assigned / counters.total) * 100) || 0;

  const handleAssign = (cuentaCodigo) => {
    if (selectedFactura) {
      onAssign(selectedFactura.id, cuentaCodigo, applyToAll ? selectedFactura.ruc : null);
      
      // Auto-jump to next unassigned
      const nextUnassigned = facturas.find(f => !f.cuenta_asignada && f.id !== selectedFactura.id);
      if (nextUnassigned) {
        setSelectedFacturaId(nextUnassigned.id);
      }
    }
  };

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-sire-dark">
      {/* Header Bar */}
      <div className="bg-sire-card border-b border-sire-secondary p-4 flex justify-between items-center shadow-md z-10">
        <div>
          <h2 className="text-xl font-bold text-sire-blue">PERIODO: {periodo || 'JULIO 2026'}</h2>
          <div className="flex space-x-4 text-sm text-gray-400 mt-1">
            <span>Facturas: {counters?.facturas || 0}</span>
            <span>Boletas: {counters?.boletas || 0}</span>
            <span>NC/ND: {counters?.ncnd || 0}</span>
          </div>
        </div>
        <div className="w-1/3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Progreso de asignación</span>
            <span className="font-bold text-sire-green">{progress}%</span>
          </div>
          <div className="w-full bg-sire-secondary rounded-full h-2.5">
            <div className="bg-sire-green h-2.5 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      </div>

      {/* Split Panel */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Facturas */}
        <div className="w-2/5 border-r border-sire-secondary flex flex-col bg-sire-dark overflow-y-auto p-4 space-y-3">
          {facturas.map(factura => (
            <FacturaCard 
              key={factura.id}
              factura={factura}
              isSelected={selectedFactura?.id === factura.id}
              isAssigned={!!factura.cuenta_asignada}
              onSelect={() => setSelectedFacturaId(factura.id)}
            />
          ))}
        </div>

        {/* Right Panel - Cuentas */}
        <div className="w-3/5 flex flex-col bg-sire-card p-6">
          {selectedFactura ? (
            <>
              <div className="bg-sire-secondary/50 rounded-xl p-4 mb-6 border border-sire-secondary">
                <h3 className="text-sm text-gray-400 mb-1">Asignando a:</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-bold text-lg text-white mr-3">{selectedFactura.serie}-{selectedFactura.numero}</span>
                    <span className="text-gray-300">{selectedFactura.ruc} - {selectedFactura.razon_social}</span>
                  </div>
                  <span className="text-xl font-bold text-sire-blue">S/ {selectedFactura.importe}</span>
                </div>
              </div>

              <div className="mb-4 flex items-center justify-between">
                <BuscadorCuentas value={searchQuery} onChange={setSearchQuery} />
              </div>
              
              <label className="flex items-center space-x-2 mb-4 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={applyToAll} 
                  onChange={(e) => setApplyToAll(e.target.checked)}
                  className="w-4 h-4 rounded text-sire-blue focus:ring-sire-blue bg-sire-dark border-gray-600"
                />
                <span className="text-sm text-gray-300">✅ Aplicar cuenta a TODAS las facturas de este RUC ({selectedFactura.ruc})</span>
              </label>

              <div className="flex-1 overflow-hidden">
                <CuentasList 
                  searchQuery={searchQuery} 
                  ruc={selectedFactura.ruc}
                  onSelect={handleAssign} 
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              Selecciona un comprobante para asignar cuenta.
            </div>
          )}
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="bg-sire-card border-t border-sire-secondary p-4 flex justify-between items-center shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] z-10">
        <div className="text-gray-400 font-medium">
          {counters?.assigned || 0} de {counters?.total || 0} asignadas
        </div>
        <button 
          onClick={onGenerate}
          disabled={counters?.assigned !== counters?.total || counters?.total === 0}
          className={`px-8 py-3 rounded-lg font-bold text-white transition shadow-lg ${
            counters?.assigned === counters?.total && counters?.total > 0
              ? 'bg-sire-green hover:bg-emerald-500 cursor-pointer' 
              : 'bg-gray-600 cursor-not-allowed'
          }`}
        >
          💾 GUARDAR Y GENERAR MACRO
        </button>
      </div>
    </div>
  );
};

export default AsignadorCuentas;

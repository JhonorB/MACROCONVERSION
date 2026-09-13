import React, { useMemo } from 'react';

// Example Mock Data - Replace with API data
const MOCK_CUENTAS = [
  { codigo: '6011001', nombre: 'MERCADERIAS' },
  { codigo: '6311001', nombre: 'TRANSPORTE DE PASAJEROS' },
  { codigo: '6311002', nombre: 'TRANSPORTE DE CARGA' },
  { codigo: '6321001', nombre: 'HONORARIOS - ASESORIA' },
  { codigo: '6361001', nombre: 'ENERGIA ELECTRICA' },
  { codigo: '6363001', nombre: 'AGUA' },
  { codigo: '6364001', nombre: 'TELEFONO E INTERNET' },
  { codigo: '6592001', nombre: 'SANCIONES ADMINISTRATIVAS' },
  { codigo: '6593001', nombre: 'GASTOS DE REPRESENTACION' },
];

const CuentasList = ({ searchQuery, ruc, onSelect }) => {
  // In a real app, you would fetch sugeridas based on RUC
  const sugeridas = useMemo(() => {
    return MOCK_CUENTAS.slice(0, 2);
  }, [ruc]);

  const filteredCuentas = useMemo(() => {
    if (!searchQuery) return MOCK_CUENTAS;
    const query = searchQuery.toLowerCase();
    return MOCK_CUENTAS.filter(c => 
      c.codigo.toLowerCase().includes(query) || 
      c.nombre.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  const highlightMatch = (text, query) => {
    if (!query) return text;
    const parts = text.toString().split(new RegExp(`(${query})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) => 
          part.toLowerCase() === query.toLowerCase() 
            ? <span key={i} className="bg-sire-blue/30 text-sire-blue">{part}</span> 
            : part
        )}
      </span>
    );
  };

  return (
    <div className="h-full overflow-y-auto pr-2 space-y-6 pb-20">
      {/* Sugeridas */}
      {!searchQuery && sugeridas.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Sugeridas por Historial</h3>
          <div className="grid grid-cols-1 gap-2">
            {sugeridas.map(cuenta => (
              <button
                key={`sug-${cuenta.codigo}`}
                onClick={() => onSelect(cuenta.codigo)}
                className="flex items-center p-3 rounded-lg border border-yellow-500/30 bg-yellow-500/5 hover:bg-yellow-500/10 hover:border-yellow-500/50 transition-colors text-left group"
              >
                <div className="w-24 font-mono font-bold text-yellow-500">{cuenta.codigo}</div>
                <div className="flex-1 text-gray-200 font-medium">{cuenta.nombre}</div>
                <span className="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-500 rounded hidden group-hover:block">Historial</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Todas las Cuentas */}
      <div>
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          {searchQuery ? 'Resultados de búsqueda' : 'Catálogo de Cuentas'}
        </h3>
        <div className="grid grid-cols-1 gap-2">
          {filteredCuentas.length > 0 ? (
            filteredCuentas.map(cuenta => (
              <button
                key={cuenta.codigo}
                onClick={() => onSelect(cuenta.codigo)}
                className="flex items-center p-3 rounded-lg border border-sire-secondary bg-sire-dark hover:bg-sire-blue/10 hover:border-sire-blue/50 transition-colors text-left"
              >
                <div className="w-24 font-mono font-bold text-sire-blue">
                  {highlightMatch(cuenta.codigo, searchQuery)}
                </div>
                <div className="flex-1 text-gray-200 font-medium">
                  {highlightMatch(cuenta.nombre, searchQuery)}
                </div>
              </button>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No se encontraron cuentas que coincidan con "{searchQuery}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CuentasList;

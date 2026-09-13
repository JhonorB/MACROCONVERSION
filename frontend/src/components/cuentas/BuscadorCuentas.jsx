import React, { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

const BuscadorCuentas = ({ value, onChange }) => {
  const [localValue, setLocalValue] = useState(value);

  // Debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(localValue);
    }, 300);
    return () => clearTimeout(timer);
  }, [localValue, onChange]);

  return (
    <div className="relative w-full max-w-md">
      <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
      <input 
        type="text" 
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder="Buscar cuenta por código o nombre..." 
        className="w-full bg-sire-dark border border-sire-secondary rounded-lg pl-10 pr-10 py-2.5 focus:outline-none focus:border-sire-blue focus:ring-1 focus:ring-sire-blue transition text-white placeholder-gray-500 shadow-inner"
      />
      {localValue && (
        <button 
          onClick={() => setLocalValue('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};

export default BuscadorCuentas;

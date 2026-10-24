import React, { useState, useRef, useEffect, useMemo } from 'react';
import { 
  MagnifyingGlassIcon, 
  ChevronUpDownIcon, 
  CheckIcon, 
  XMarkIcon,
  BuildingOffice2Icon
} from '@heroicons/react/24/outline';

const normalizeText = (text) => {
  if (!text) return '';
  return text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
    .trim();
};

export const EmpresaCombobox = ({
  empresas = [],
  selectedId = '',
  onSelect,
  loading = false,
  placeholder = 'Buscar empresa por RUC o Razón Social...'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef(null);
  const searchInputRef = useRef(null);

  // Find currently selected empresa object
  const selectedEmpresa = useMemo(() => {
    if (!selectedId) return null;
    return empresas.find(e => String(e.id) === String(selectedId)) || null;
  }, [empresas, selectedId]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when opened
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  // Filtered empresas
  const filteredEmpresas = useMemo(() => {
    if (!search.trim()) return empresas;
    const term = normalizeText(search);
    return empresas.filter(emp => {
      const rucMatch = emp.ruc && emp.ruc.includes(term);
      const nameMatch = normalizeText(emp.razon_social).includes(term);
      const codMatch = emp.codigo && normalizeText(emp.codigo).includes(term);
      return rucMatch || nameMatch || codMatch;
    });
  }, [empresas, search]);

  const handleSelect = (empresa) => {
    onSelect(empresa ? empresa.id : '');
    setIsOpen(false);
    setSearch('');
  };

  const handleClear = (e) => {
    e.stopPropagation();
    onSelect('');
    setSearch('');
  };

  return (
    <div className="relative w-full" ref={containerRef}>
      {/* Trigger Button */}
      <div
        onClick={() => setIsOpen(prev => !prev)}
        className={`w-full bg-sire-dark border rounded-lg px-3 py-2 text-left cursor-pointer flex items-center justify-between transition-all duration-200 select-none ${
          isOpen 
            ? 'border-sire-blue ring-2 ring-sire-blue/20' 
            : 'border-sire-secondary hover:border-gray-500'
        }`}
      >
        <div className="flex items-center space-x-2 min-w-0 flex-1 mr-2">
          <BuildingOffice2Icon className="h-5 w-5 text-gray-400 shrink-0" />
          {selectedEmpresa ? (
            <div className="flex items-center space-x-2 min-w-0 flex-1">
              <span className="font-mono text-xs bg-sire-blue/20 text-sire-blue border border-sire-blue/30 px-2 py-0.5 rounded font-semibold shrink-0">
                {selectedEmpresa.ruc}
              </span>
              <span className="text-white text-sm font-medium truncate" title={selectedEmpresa.razon_social}>
                {selectedEmpresa.razon_social}
              </span>
              {selectedEmpresa.codigo && (
                <span className="text-[10px] text-gray-400 bg-gray-800 px-1.5 py-0.5 rounded shrink-0">
                  COD: {selectedEmpresa.codigo}
                </span>
              )}
            </div>
          ) : (
            <span className="text-gray-400 text-sm truncate">
              {loading ? 'Cargando empresas...' : placeholder}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-1 shrink-0">
          {selectedEmpresa && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white transition-colors"
              title="Quitar selección"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          )}
          <ChevronUpDownIcon className="h-4 w-4 text-gray-400" />
        </div>
      </div>

      {/* Floating Dropdown Panel */}
      {isOpen && (
        <div className="absolute left-0 right-0 mt-1 z-50 bg-sire-card border border-sire-secondary rounded-xl shadow-2xl overflow-hidden backdrop-blur-md">
          {/* Search Input Bar */}
          <div className="p-3 border-b border-sire-secondary/60 bg-sire-dark/70">
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Escribe RUC o nombre de empresa..."
                className="w-full bg-sire-dark border border-sire-secondary rounded-lg pl-9 pr-8 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sire-blue focus:ring-1 focus:ring-sire-blue transition-all"
              />
              {search && (
                <button
                  type="button"
                  onClick={() => setSearch('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              )}
            </div>
            
            <div className="flex justify-between items-center mt-2 px-1 text-xs text-gray-400">
              <span>{filteredEmpresas.length} {filteredEmpresas.length === 1 ? 'empresa encontrada' : 'empresas encontradas'}</span>
              {search && (
                <button
                  type="button"
                  onClick={() => setSearch('')}
                  className="text-sire-blue hover:underline text-xs"
                >
                  Limpiar filtro
                </button>
              )}
            </div>
          </div>

          {/* List of Empresas */}
          <div className="max-h-64 overflow-y-auto divide-y divide-sire-secondary/30 custom-scrollbar">
            {loading ? (
              <div className="p-6 text-center text-sm text-gray-400">
                <div className="w-6 h-6 border-2 border-sire-blue border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                Cargando empresas...
              </div>
            ) : filteredEmpresas.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-400">
                <BuildingOffice2Icon className="h-8 w-8 text-gray-500 mx-auto mb-2 opacity-50" />
                <p>No se encontraron empresas con "{search}".</p>
                <p className="text-xs text-gray-500 mt-1">Prueba buscando por los primeros dígitos del RUC o una palabra clave.</p>
              </div>
            ) : (
              filteredEmpresas.map((emp) => {
                const isSelected = String(emp.id) === String(selectedId);
                return (
                  <div
                    key={emp.id}
                    onClick={() => handleSelect(emp)}
                    className={`px-3 py-2.5 cursor-pointer transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-sire-blue/15 text-white border-l-4 border-sire-blue'
                        : 'hover:bg-slate-800/80 text-gray-200'
                    }`}
                  >
                    <div className="min-w-0 flex-1 pr-2">
                      <div className="flex items-center space-x-2">
                        <span className={`font-mono text-xs px-2 py-0.5 rounded font-bold ${
                          isSelected ? 'bg-sire-blue text-white' : 'bg-sire-secondary text-sire-blue'
                        }`}>
                          {emp.ruc}
                        </span>
                        {emp.codigo && (
                          <span className="text-[10px] text-gray-400 bg-gray-900 border border-gray-700 px-1.5 py-0.5 rounded font-mono">
                            COD: {emp.codigo}
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-medium mt-1 leading-snug line-clamp-2">
                        {emp.razon_social}
                      </p>
                    </div>

                    {isSelected && (
                      <CheckIcon className="h-5 w-5 text-sire-blue shrink-0 ml-2" />
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmpresaCombobox;

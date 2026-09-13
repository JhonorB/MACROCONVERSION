import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  ArrowUpTrayIcon, 
  MagnifyingGlassIcon, 
  CheckCircleIcon,
  XMarkIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth';
import { useEmpresas } from '../../hooks/useEmpresas';
import EmpresaModal from '../empresas/EmpresaModal';

const Dashboard = ({ onProcess }) => {
  const { rol } = useAuth();
  const {
    empresas,
    loading,
    selectedEmpresa,
    searchQuery,
    setSearchQuery,
    setSelectedEmpresa,
    addEmpresa,
    editEmpresa,
    removeEmpresa
  } = useEmpresas();

  const [file, setFile] = useState(null);
  const [tipoRegistro, setTipoRegistro] = useState('COM');
  const [subtipoVta, setSubtipoVta] = useState('MERCADERIA');
  
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  
  const [mes, setMes] = useState(currentMonth === 0 ? '12' : currentMonth.toString().padStart(2, '0'));
  const [anio, setAnio] = useState((currentMonth === 0 ? currentYear - 1 : currentYear).toString().slice(-2));

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [empresaToEdit, setEmpresaToEdit] = useState(null);

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles?.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'text/plain': ['.txt']
    },
    maxFiles: 1
  });

  const isFormValid = file && selectedEmpresa && anio.length === 2 && mes.length === 2;

  const handleGenerate = () => {
    if (!isFormValid) return;
    onProcess({ file, empresaId: selectedEmpresa.id, tipo: tipoRegistro, subtipoVta: tipoRegistro === 'VTA' ? subtipoVta : null, anio, mes });
  };

  const handleOpenModal = (empresa = null) => {
    setEmpresaToEdit(empresa);
    setIsModalOpen(true);
  };

  const handleSaveEmpresa = async (data) => {
    if (empresaToEdit) {
      await editEmpresa(empresaToEdit.id, data);
    } else {
      await addEmpresa(data);
    }
    setIsModalOpen(false);
  };

  const handleDeleteEmpresa = async (empresa, e) => {
    e.stopPropagation();
    if (window.confirm(`¿Está seguro de eliminar esta empresa: ${empresa.ruc} - ${empresa.razon_social}?`)) {
      await removeEmpresa(empresa.id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column - Main Form */}
      <div className="lg:col-span-2 space-y-6">
        {/* Upload Section */}
        <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
          <h2 className="text-lg font-semibold mb-4">📄 Archivo SIRE</h2>
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all duration-200 ${
              isDragActive ? 'border-sire-blue bg-sire-blue/10' : 'border-gray-600 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="flex flex-col items-center text-sire-green">
                <CheckCircleIcon className="w-12 h-12 mb-2" />
                <p className="font-medium text-white">{file.name}</p>
                <p className="text-sm text-gray-400 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
            ) : (
              <div className="flex flex-col items-center text-gray-400">
                <ArrowUpTrayIcon className="w-12 h-12 mb-2" />
                <p className="text-white">Arrastra tu archivo CSV del SIRE aquí</p>
                <p className="text-sm mt-1">o haz clic para seleccionar</p>
              </div>
            )}
          </div>
        </div>

        {/* Empresa Selector */}
        <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">🏢 Empresa</h2>
            {rol === 'ADMIN' && (
              <button 
                onClick={() => handleOpenModal()}
                className="text-sm bg-sire-green/20 text-sire-green hover:bg-sire-green/30 px-3 py-1 rounded transition"
              >
                ➕ Nueva
              </button>
            )}
          </div>
          <div className="relative mb-4">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Buscar empresa..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-sire-dark border border-sire-secondary rounded-lg pl-10 pr-10 py-2 focus:outline-none focus:border-sire-blue transition"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors flex items-center gap-1 text-sm bg-sire-card px-2 py-1 rounded"
              >
                <XMarkIcon className="w-4 h-4" /> Limpiar
              </button>
            )}
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
            {loading ? (
              <div className="text-center py-4 text-gray-400">Cargando empresas...</div>
            ) : empresas.length === 0 ? (
              <div className="text-center py-4 text-gray-400">No se encontraron empresas.</div>
            ) : (
              empresas.map((empresa) => (
                <div 
                  key={empresa.id}
                  onClick={() => setSelectedEmpresa(empresa)}
                  className={`p-3 rounded-lg border cursor-pointer transition group flex justify-between items-center ${
                    selectedEmpresa?.id === empresa.id ? 'border-sire-blue bg-sire-blue/10' : 'border-sire-secondary hover:border-gray-600'
                  }`}
                >
                  <div>
                    <div className="flex gap-3 items-center">
                      <span className="font-medium">{empresa.ruc}</span>
                      {empresa.codigo && <span className="text-gray-400 text-sm">COD: {empresa.codigo}</span>}
                    </div>
                    <p className="text-sm text-gray-300 mt-1">{empresa.razon_social}</p>
                  </div>
                  
                  {rol === 'ADMIN' && (
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={(e) => { e.stopPropagation(); handleOpenModal(empresa); }}
                        className="p-2 text-gray-400 hover:text-sire-blue hover:bg-sire-blue/10 rounded"
                        title="Editar"
                      >
                        <PencilIcon className="w-5 h-5" />
                      </button>
                      <button 
                        onClick={(e) => handleDeleteEmpresa(empresa, e)}
                        className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded"
                        title="Eliminar"
                      >
                        <TrashIcon className="w-5 h-5" />
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Tipo y Periodo */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
            <h2 className="text-lg font-semibold mb-4">Tipo de Registro</h2>
            <div className="flex space-x-4">
              <button 
                onClick={() => setTipoRegistro('COM')}
                className={`flex-1 py-3 rounded-lg border flex flex-col items-center transition ${
                  tipoRegistro === 'COM' ? 'border-sire-blue bg-sire-blue/20 text-sire-blue' : 'border-sire-secondary text-gray-400 hover:border-gray-500'
                }`}
              >
                <span className="text-2xl mb-1">📥</span>
                <span className="font-semibold">Compras (COM)</span>
              </button>
              <button 
                onClick={() => setTipoRegistro('VTA')}
                className={`flex-1 py-3 rounded-lg border flex flex-col items-center transition ${
                  tipoRegistro === 'VTA' ? 'border-sire-green bg-sire-green/20 text-sire-green' : 'border-sire-secondary text-gray-400 hover:border-gray-500'
                }`}
              >
                <span className="text-2xl mb-1">📤</span>
                <span className="font-semibold">Ventas (VTA)</span>
              </button>
            </div>
            {tipoRegistro === 'VTA' && (
              <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mt-4">
                <select 
                  value={subtipoVta} 
                  onChange={(e) => setSubtipoVta(e.target.value)}
                  className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2 focus:outline-none focus:border-sire-green transition"
                >
                  <option value="MERCADERIA">MERCADERIA</option>
                  <option value="PRODUCTOS TERMINADOS">PRODUCTOS TERMINADOS</option>
                  <option value="SERVICIOS">SERVICIOS</option>
                </select>
              </motion.div>
            )}
          </div>

          <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
            <h2 className="text-lg font-semibold mb-4">Periodo</h2>
            <div className="flex space-x-4">
              <div className="flex-1">
                <label className="block text-sm text-gray-400 mb-1">Mes (MM)</label>
                <input 
                  type="text" 
                  maxLength={2}
                  value={mes}
                  onChange={(e) => setMes(e.target.value)}
                  className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2 focus:outline-none focus:border-sire-blue text-center text-lg transition"
                />
              </div>
              <div className="flex-1">
                <label className="block text-sm text-gray-400 mb-1">Año (YY)</label>
                <input 
                  type="text" 
                  maxLength={2}
                  value={anio}
                  onChange={(e) => setAnio(e.target.value)}
                  className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2 focus:outline-none focus:border-sire-blue text-center text-lg transition"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <motion.button
          whileHover={{ scale: isFormValid ? 1.02 : 1 }}
          whileTap={{ scale: isFormValid ? 0.98 : 1 }}
          onClick={handleGenerate}
          disabled={!isFormValid}
          className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-colors ${
            isFormValid 
              ? 'bg-sire-green hover:bg-emerald-500 text-white cursor-pointer' 
              : 'bg-sire-secondary text-gray-500 cursor-not-allowed'
          }`}
        >
          🚀 GENERAR MACRO EXCEL
        </motion.button>
      </div>

      {/* Right Column - Sidebar Info */}
      <div className="space-y-6">
        <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
          <h2 className="text-lg font-semibold mb-4 border-b border-sire-secondary pb-2">ℹ️ Instrucciones</h2>
          <ul className="space-y-3 text-sm text-gray-300">
            <li className="flex items-start"><span className="mr-2 text-sire-blue">•</span> Sube el archivo CSV o TXT descargado del SIRE SUNAT.</li>
            <li className="flex items-start"><span className="mr-2 text-sire-blue">•</span> Selecciona la empresa a la que corresponde.</li>
            <li className="flex items-start"><span className="mr-2 text-sire-blue">•</span> El sistema detectará automáticamente las detracciones.</li>
            <li className="flex items-start"><span className="mr-2 text-sire-blue">•</span> Para compras, se te pedirá asignar cuentas contables.</li>
          </ul>
        </div>
        
        <div className="bg-sire-card rounded-xl p-6 shadow-lg border border-sire-secondary">
          <h2 className="text-lg font-semibold mb-4 border-b border-sire-secondary pb-2">📊 Estadísticas Rápidas</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Procesos hoy</span>
              <span className="font-bold text-lg">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Empresas registradas</span>
              <span className="font-bold text-lg">{empresas.length}</span>
            </div>
          </div>
        </div>
      </div>

      <EmpresaModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveEmpresa}
        empresa={empresaToEdit}
      />
    </div>
  );
};

export default Dashboard;

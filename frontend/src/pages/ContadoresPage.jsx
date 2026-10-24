import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import * as api from '../api/client';
import toast from 'react-hot-toast';
import { 
  MagnifyingGlassIcon, 
  PlusIcon,
  PencilSquareIcon,
  EyeIcon,
  TrashIcon,
  PowerIcon
} from '@heroicons/react/24/outline';
import ContadorModal from '../components/admin/ContadorModal';

const ContadoresPage = () => {
  const [contadores, setContadores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedContador, setSelectedContador] = useState(null);
  const navigate = useNavigate();

  const fetchContadores = async () => {
    try {
      setLoading(true);
      const res = await api.getContadores();
      setContadores(res.data.results || res.data || []);
    } catch (error) {
      toast.error('Error al cargar contadores');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContadores();
  }, []);

  const handleEdit = (contador) => {
    setSelectedContador(contador);
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedContador(null);
    setIsModalOpen(true);
  };

  const handleViewDetails = (id) => {
    navigate(`/admin/contadores/${id}`);
  };

  const handleToggleEstado = async (id, currentEstado) => {
    const accion = currentEstado === 'ACTIVO' ? 'desactivar' : 'activar';
    if (window.confirm(`¿Está seguro de ${accion} este contador?`)) {
      try {
        await api.activarContador(id);
        toast.success(`Contador ${accion === 'desactivar' ? 'desactivado' : 'activado'} exitosamente`);
        fetchContadores();
      } catch (error) {
        toast.error('Error al cambiar estado del contador');
      }
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Está seguro de eliminar este contador? Esta acción no se puede deshacer.')) {
      try {
        await api.deleteContador(id);
        toast.success('Contador eliminado exitosamente');
        fetchContadores();
      } catch (error) {
        toast.error('Error al eliminar contador');
      }
    }
  };

  const filteredContadores = contadores.filter(c => 
    c.first_name?.toLowerCase().includes(search.toLowerCase()) || 
    c.last_name?.toLowerCase().includes(search.toLowerCase()) || 
    c.username.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
            <span className="mr-3">👥</span> Gestión de Contadores
          </h1>
          <p className="text-gray-400">Administra los usuarios contadores del sistema</p>
        </div>
        
        <div className="flex w-full md:w-auto space-x-3">
          <div className="relative flex-grow md:w-64">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar contador..."
              className="w-full pl-10 pr-4 py-2.5 bg-sire-card border border-sire-secondary rounded-lg text-white focus:outline-none focus:border-sire-blue focus:ring-1 focus:ring-sire-blue transition-all"
            />
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2.5 bg-sire-green hover:bg-emerald-500 text-white font-medium rounded-lg shadow-lg shadow-sire-green/20 transition-all focus:ring-2 focus:ring-offset-2 focus:ring-offset-sire-dark focus:ring-sire-green cursor-pointer"
          >
            <PlusIcon className="w-5 h-5 mr-2" />
            Nuevo Contador
          </button>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sire-blue"></div>
        </div>
      ) : filteredContadores.length === 0 ? (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-sire-card border border-sire-secondary rounded-xl p-12 text-center"
        >
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-white mb-2">No hay contadores registrados</h3>
          <p className="text-gray-400 max-w-md mx-auto">
            {search ? 'No se encontraron resultados para tu búsqueda.' : 'Crea tu primer contador usando el botón "Nuevo Contador".'}
          </p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredContadores.map((contador) => {
              const estado = contador.estado || contador.perfil?.estado || (contador.is_active ? 'ACTIVO' : 'INACTIVO');
              const telefono = contador.telefono || contador.perfil?.telefono || '-';
              const empresasCount = contador.empresas_count ?? contador.empresa_count ?? 0;
              const procesosCount = contador.procesos_count ?? contador.proceso_count ?? 0;

              return (
                <motion.div
                  key={contador.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-sire-card border border-sire-secondary rounded-xl overflow-hidden hover:shadow-xl transition-all hover:border-sire-blue/50 group flex flex-col"
                >
                  <div className="p-6 flex-grow">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-sire-blue to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-inner">
                          {contador.first_name ? contador.first_name.charAt(0).toUpperCase() : contador.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-white truncate max-w-[150px]" title={`${contador.first_name} ${contador.last_name}`}>
                            {contador.first_name} {contador.last_name}
                          </h3>
                          <p className="text-sm text-gray-400">@{contador.username}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-bold rounded flex items-center ${
                        estado === 'ACTIVO' ? 'bg-sire-green/20 text-sire-green border border-sire-green/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}>
                        {estado === 'ACTIVO' ? '✓ ACTIVO' : '✕ INACTIVO'}
                      </span>
                    </div>

                    <div className="space-y-2 mt-4 text-sm text-gray-300">
                      <div className="flex justify-between border-b border-sire-secondary/50 pb-2">
                        <span className="text-gray-500">Email:</span>
                        <span className="truncate ml-2 text-white font-medium" title={contador.email}>{contador.email || '-'}</span>
                      </div>
                      <div className="flex justify-between border-b border-sire-secondary/50 pb-2">
                        <span className="text-gray-500">Teléfono:</span>
                        <span className="text-white font-medium">{telefono}</span>
                      </div>
                      <div className="flex justify-between pb-1">
                        <span className="text-gray-500">Actividad:</span>
                        <span className="font-medium text-sire-blue">{empresasCount} empresas, {procesosCount} proc.</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-sire-dark/50 border-t border-sire-secondary p-3 flex justify-between gap-2">
                    <button
                      onClick={() => handleViewDetails(contador.id)}
                      className="flex-1 flex items-center justify-center py-1.5 px-2 bg-sire-card hover:bg-sire-secondary/50 border border-sire-secondary rounded text-gray-300 text-xs font-medium transition-colors cursor-pointer"
                      title="Ver Detalle"
                    >
                      <EyeIcon className="w-4 h-4 mr-1.5" /> Detalle
                    </button>
                    <button
                      onClick={() => handleEdit(contador)}
                      className="flex-1 flex items-center justify-center py-1.5 px-2 bg-sire-card hover:bg-sire-secondary/50 border border-sire-secondary rounded text-blue-400 text-xs font-medium transition-colors cursor-pointer"
                      title="Editar"
                    >
                      <PencilSquareIcon className="w-4 h-4 mr-1.5" /> Editar
                    </button>
                    <button
                      onClick={() => handleToggleEstado(contador.id, estado)}
                      className={`flex-1 flex items-center justify-center py-1.5 px-2 bg-sire-card hover:bg-sire-secondary/50 border border-sire-secondary rounded text-xs font-medium transition-colors cursor-pointer ${
                        estado === 'ACTIVO' ? 'text-amber-400 hover:text-amber-300' : 'text-sire-green hover:text-emerald-400'
                      }`}
                      title={estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                    >
                      <PowerIcon className="w-4 h-4 mr-1.5" /> {estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                    </button>
                    <button
                      onClick={() => handleDelete(contador.id)}
                      className="flex items-center justify-center py-1.5 px-3 bg-sire-card hover:bg-red-500/20 border border-sire-secondary hover:border-red-500/50 rounded text-red-400 text-xs font-medium transition-colors cursor-pointer"
                      title="Eliminar"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      {isModalOpen && (
        <ContadorModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          contador={selectedContador}
          onSuccess={fetchContadores}
        />
      )}
    </div>
  );
};

export default ContadoresPage;

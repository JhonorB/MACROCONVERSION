import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/outline';
import * as api from '../../api/client';
import toast from 'react-hot-toast';

const ContadorModal = ({ isOpen, onClose, contador, onSuccess }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    telefono: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (contador) {
      setFormData({
        first_name: contador.first_name || '',
        last_name: contador.last_name || '',
        username: contador.username || '',
        email: contador.email || '',
        password: '',
        telefono: contador.telefono || ''
      });
    } else {
      setFormData({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        telefono: ''
      });
    }
    setErrors({});
  }, [contador, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.first_name) newErrors.first_name = 'El nombre es requerido';
    if (!formData.last_name) newErrors.last_name = 'El apellido es requerido';
    if (!contador && !formData.username) newErrors.username = 'El usuario es requerido';
    if (!contador && !formData.password) newErrors.password = 'La contraseña es requerida';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setLoading(true);
      const dataToSubmit = { ...formData };
      if (contador && !dataToSubmit.password) {
        delete dataToSubmit.password;
      }
      
      if (contador) {
        await api.updateContador(contador.id, dataToSubmit);
        toast.success('Contador actualizado exitosamente');
      } else {
        await api.createContador(dataToSubmit);
        toast.success('Contador creado exitosamente');
      }
      onSuccess();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al guardar el contador');
      if (error.response?.data?.details) {
        setErrors(error.response.data.details);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-sire-card w-full max-w-lg rounded-2xl border border-sire-secondary shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        >
          <div className="flex justify-between items-center p-6 border-b border-sire-secondary bg-sire-dark/50">
            <h2 className="text-xl font-bold text-white">
              {contador ? '✏️ Editar Contador' : '➕ Nuevo Contador'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto flex-grow custom-scrollbar">
            <form id="contador-form" onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Nombre *</label>
                  <input
                    type="text" name="first_name" value={formData.first_name} onChange={handleChange}
                    className={`w-full px-4 py-2 bg-sire-dark border ${errors.first_name ? 'border-red-500' : 'border-sire-secondary'} rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all`}
                    placeholder="Nombres"
                  />
                  {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Apellido *</label>
                  <input
                    type="text" name="last_name" value={formData.last_name} onChange={handleChange}
                    className={`w-full px-4 py-2 bg-sire-dark border ${errors.last_name ? 'border-red-500' : 'border-sire-secondary'} rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all`}
                    placeholder="Apellidos"
                  />
                  {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Nombre de usuario {contador ? '' : '*'}</label>
                <input
                  type="text" name="username" value={formData.username} onChange={handleChange} disabled={!!contador}
                  className={`w-full px-4 py-2 bg-sire-dark border ${errors.username ? 'border-red-500' : 'border-sire-secondary'} rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all ${contador ? 'opacity-50 cursor-not-allowed' : ''}`}
                  placeholder="usuario_sistema"
                />
                {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Correo electrónico</label>
                <input
                  type="email" name="email" value={formData.email} onChange={handleChange}
                  className="w-full px-4 py-2 bg-sire-dark border border-sire-secondary rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all"
                  placeholder="correo@ejemplo.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Contraseña {contador ? '(Opcional)' : '*'}</label>
                <input
                  type="password" name="password" value={formData.password} onChange={handleChange}
                  className={`w-full px-4 py-2 bg-sire-dark border ${errors.password ? 'border-red-500' : 'border-sire-secondary'} rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all`}
                  placeholder={contador ? 'Dejar en blanco para mantener actual' : '••••••••'}
                />
                {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Teléfono</label>
                <input
                  type="text" name="telefono" value={formData.telefono} onChange={handleChange}
                  className="w-full px-4 py-2 bg-sire-dark border border-sire-secondary rounded-lg text-white focus:ring-2 focus:ring-sire-blue focus:border-transparent outline-none transition-all"
                  placeholder="987654321"
                />
              </div>
            </form>
          </div>

          <div className="p-6 border-t border-sire-secondary bg-sire-dark/30 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-5 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-sire-secondary/50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              form="contador-form"
              disabled={loading}
              className="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-sire-blue hover:bg-blue-500 focus:ring-2 focus:ring-offset-2 focus:ring-offset-sire-dark focus:ring-sire-blue transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>}
              {contador ? 'Guardar Cambios' : 'Crear Contador'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ContadorModal;

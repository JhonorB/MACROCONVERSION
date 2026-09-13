import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/outline';

const EmpresaModal = ({ isOpen, onClose, onSave, empresa }) => {
  const [formData, setFormData] = useState({
    codigo: '',
    ruc: '',
    razon_social: ''
  });

  useEffect(() => {
    if (empresa) {
      setFormData({
        codigo: empresa.codigo || '',
        ruc: empresa.ruc || '',
        razon_social: empresa.razon_social || ''
      });
    } else {
      setFormData({ codigo: '', ruc: '', razon_social: '' });
    }
  }, [empresa]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-md bg-sire-dark border border-sire-secondary rounded-xl shadow-2xl p-6 overflow-hidden"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">
                {empresa ? '✏️ Editar Empresa' : '🏢 Nueva Empresa'}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Código (Opcional)
                </label>
                <input
                  type="text"
                  name="codigo"
                  value={formData.codigo}
                  onChange={handleChange}
                  className="w-full bg-sire-card border border-sire-secondary rounded-lg px-4 py-2 text-white focus:outline-none focus:border-sire-blue transition-colors"
                  placeholder="Ej. 01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  RUC
                </label>
                <input
                  type="text"
                  name="ruc"
                  required
                  maxLength={11}
                  value={formData.ruc}
                  onChange={handleChange}
                  className="w-full bg-sire-card border border-sire-secondary rounded-lg px-4 py-2 text-white focus:outline-none focus:border-sire-blue transition-colors"
                  placeholder="Ej. 20123456789"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Razón Social
                </label>
                <input
                  type="text"
                  name="razon_social"
                  required
                  value={formData.razon_social}
                  onChange={handleChange}
                  className="w-full bg-sire-card border border-sire-secondary rounded-lg px-4 py-2 text-white focus:outline-none focus:border-sire-blue transition-colors"
                  placeholder="Ej. MI EMPRESA SAC"
                />
              </div>

              <div className="pt-4 flex space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-2 px-4 bg-sire-card border border-sire-secondary rounded-lg text-white hover:bg-gray-700 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 px-4 bg-sire-blue hover:bg-blue-600 rounded-lg text-white font-medium transition-colors"
                >
                  Guardar
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default EmpresaModal;

import { useState, useEffect } from 'react';
import * as api from '../api/client';
import { showToast } from '../components/layout/Toast';

export const useEmpresas = () => {
  const [empresas, setEmpresas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEmpresa, setSelectedEmpresa] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchEmpresas = async () => {
      try {
        setLoading(true);
        const { data } = await api.getEmpresas(searchQuery);
        setEmpresas(data.results || data);
        setError(null);
      } catch (err) {
        setError(err.message);
        showToast.error('Error al cargar empresas');
      } finally {
        setLoading(false);
      }
    };
    fetchEmpresas();
  }, [searchQuery]);

  const addEmpresa = async (empresaData) => {
    try {
      const { data } = await api.createEmpresa(empresaData);
      setEmpresas(prev => [...prev, data]);
      showToast.success('Empresa creada correctamente');
      return data;
    } catch (err) {
      showToast.error('Error al crear empresa');
      throw err;
    }
  };

  const editEmpresa = async (id, empresaData) => {
    try {
      const { data } = await api.updateEmpresa(id, empresaData);
      setEmpresas(prev => prev.map(e => (e.id === id ? data : e)));
      if (selectedEmpresa?.id === id) {
        setSelectedEmpresa(data);
      }
      showToast.success('Empresa actualizada correctamente');
      return data;
    } catch (err) {
      showToast.error('Error al actualizar empresa');
      throw err;
    }
  };

  const removeEmpresa = async (id) => {
    try {
      await api.deleteEmpresa(id);
      setEmpresas(prev => prev.filter(e => e.id !== id));
      if (selectedEmpresa?.id === id) setSelectedEmpresa(null);
      showToast.success('Empresa eliminada');
    } catch (err) {
      showToast.error('Error al eliminar empresa');
      throw err;
    }
  };

  return {
    empresas,
    loading,
    error,
    selectedEmpresa,
    searchQuery,
    setSearchQuery,
    setSelectedEmpresa,
    addEmpresa,
    editEmpresa,
    removeEmpresa,
  };
};

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { UserIcon, LockClosedIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error('Por favor ingrese usuario y contraseña');
      return;
    }
    
    const result = await login(username, password);
    if (result.success) {
      if (result.user?.estado === 'INACTIVO') {
        toast.error('Su cuenta ha sido desactivada. Contacte al administrador.');
        // Opcional: logout() si es necesario forzar la salida
        return;
      }
      toast.success(`Bienvenido, ${result.user?.rol === 'ADMIN' ? 'Administrador' : 'Contador'}`);
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } else {
      toast.error(result.error);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F1117] flex flex-col items-center justify-center relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
        <motion.div 
          animate={{ 
            opacity: [0.1, 0.3, 0.1],
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -50, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-sire-blue/20 blur-[120px]"
        />
        <motion.div 
          animate={{ 
            opacity: [0.1, 0.2, 0.1],
            scale: [1, 1.5, 1],
            x: [0, -50, 0],
            y: [0, 50, 0]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute bottom-[10%] -right-[10%] w-[40%] h-[40%] rounded-full bg-sire-green/20 blur-[100px]"
        />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md bg-[#1A1D26] p-8 rounded-2xl shadow-2xl border border-sire-secondary z-10 relative"
      >
        <div className="text-center mb-8">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
            className="text-5xl mb-4"
          >
            📊
          </motion.div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#1877F2] to-[#2FA572] bg-clip-text text-transparent mb-2">
            Conversor SIRE
          </h1>
          <p className="text-gray-400 text-sm">Sistema de Conversión SIRE → CONCAR</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-1"
          >
            <label className="text-sm font-medium text-gray-300 ml-1">Usuario</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <UserIcon className="h-5 w-5 text-gray-500" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="block w-full pl-10 pr-3 py-3 border border-sire-secondary rounded-xl bg-sire-dark text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sire-blue focus:border-transparent transition-all"
                placeholder="Ingrese su usuario"
              />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="space-y-1"
          >
            <label className="text-sm font-medium text-gray-300 ml-1">Contraseña</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <LockClosedIcon className="h-5 w-5 text-gray-500" />
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-10 pr-10 py-3 border border-sire-secondary rounded-xl bg-sire-dark text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sire-blue focus:border-transparent transition-all"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-300 transition-colors"
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-5 w-5" />
                ) : (
                  <EyeIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-[#2FA572] hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-sire-dark focus:ring-sire-green transition-all mt-4"
          >
            {loading ? (
              <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Iniciar Sesión'
            )}
          </motion.button>
        </form>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center"
        >
          <p className="text-xs text-gray-500">
            Usuario: admin | Contraseña: admin123
          </p>
        </motion.div>
      </motion.div>
      
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="absolute bottom-6 text-gray-500 text-sm font-medium z-10"
      >
        v2.0 — Docker Edition
      </motion.div>
    </div>
  );
};

export default LoginPage;

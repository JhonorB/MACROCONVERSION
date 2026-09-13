import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';

const Header = () => {
  const { user, logout, rol } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const username = user?.username || 'Usuario';
  const initial = username.charAt(0).toUpperCase();
  const isAdmin = rol === 'ADMIN';

  return (
    <header className="sticky top-0 z-50 bg-sire-dark/90 backdrop-blur-md border-b border-sire-secondary">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">📊</span>
            <h1 className="text-xl font-bold bg-gradient-to-r from-sire-blue to-sire-green bg-clip-text text-transparent">
              Conversor SIRE
            </h1>
          </div>
          
          <nav className="hidden md:flex space-x-1">
            <NavLink 
              to="/" 
              className={({ isActive }) => `px-4 py-2 rounded-lg font-medium transition-colors ${isActive ? 'bg-sire-blue/10 text-sire-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-sire-card'}`}
              end
            >
              Dashboard
            </NavLink>
            <NavLink 
              to="/proceso" 
              className={({ isActive }) => `px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-1 ${isActive ? 'bg-sire-blue/10 text-sire-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-sire-card'}`}
            >
              🔄 Conversor
            </NavLink>
            <NavLink 
              to="/impuestos" 
              className={({ isActive }) => `px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-1 ${isActive ? 'bg-sire-blue/10 text-sire-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-sire-card'}`}
            >
              🧮 Calcular Impuestos
            </NavLink>
            {isAdmin && (
              <>
                <NavLink 
                  to="/admin/contadores" 
                  className={({ isActive }) => `px-4 py-2 rounded-lg font-medium transition-colors flex items-center ${isActive ? 'bg-sire-blue/10 text-sire-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-sire-card'}`}
                >
                  👥 Contadores
                </NavLink>
                <NavLink 
                  to="/admin/liquidacion" 
                  className={({ isActive }) => `px-4 py-2 rounded-lg font-medium transition-colors flex items-center ${isActive ? 'bg-sire-blue/10 text-sire-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-sire-card'}`}
                >
                  🧾 Liquidación
                </NavLink>
              </>
            )}
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2">
            {isAdmin ? (
              <span className="px-2 py-1 text-[10px] uppercase tracking-wider font-bold bg-red-500/20 text-red-500 border border-red-500/30 rounded flex items-center">
                🔑 ADMIN
              </span>
            ) : (
              <span className="px-2 py-1 text-[10px] uppercase tracking-wider font-bold bg-sire-blue/20 text-sire-blue border border-sire-blue/30 rounded flex items-center">
                📊 CONTADOR
              </span>
            )}
          </div>

          {/* User Menu */}
          <div className="relative">
            <button 
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-sire-blue to-purple-600 text-white font-bold shadow-md hover:shadow-lg transition-all focus:outline-none focus:ring-2 focus:ring-sire-blue focus:ring-offset-2 focus:ring-offset-sire-dark"
            >
              {initial}
            </button>
            
            <AnimatePresence>
              {dropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setDropdownOpen(false)}
                  ></div>
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-48 bg-sire-card border border-sire-secondary rounded-xl shadow-xl z-50 overflow-hidden"
                  >
                    <div className="px-4 py-3 border-b border-sire-secondary bg-sire-dark/50">
                      <p className="text-sm text-white font-medium truncate">{username}</p>
                      <p className="text-xs text-gray-400 truncate">{isAdmin ? 'Administrador' : 'Contador'}</p>
                    </div>
                    <div className="py-1">
                      <button 
                        disabled
                        className="w-full flex items-center px-4 py-2 text-sm text-gray-400 opacity-50 cursor-not-allowed"
                      >
                        <UserCircleIcon className="mr-3 h-5 w-5" />
                        👤 Mi Perfil
                      </button>
                      <button 
                        onClick={handleLogout}
                        className="w-full flex items-center px-4 py-2 text-sm text-red-400 hover:bg-red-400/10 hover:text-red-300 transition-colors"
                      >
                        <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
                        🚪 Cerrar Sesión
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
      <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-sire-blue/30 to-transparent"></div>
    </header>
  );
};

export default Header;

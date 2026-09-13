import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './App.jsx';
import { AuthProvider } from './hooks/useAuth.jsx';
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster 
          position="top-right"
          toastOptions={{
            style: {
              background: '#1A1D26',
              color: '#fff',
              border: '1px solid #262C36',
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);

import { toast } from 'react-hot-toast';

export const showToast = {
  success: (message) => toast.success(message, {
    iconTheme: {
      primary: '#2FA572',
      secondary: '#fff',
    },
  }),
  error: (message) => toast.error(message, {
    iconTheme: {
      primary: '#E74C3C',
      secondary: '#fff',
    },
  }),
  loading: (message) => toast.loading(message),
  dismiss: (id) => toast.dismiss(id),
};

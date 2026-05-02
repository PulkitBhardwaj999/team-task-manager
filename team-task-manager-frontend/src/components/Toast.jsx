import { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react';

export function Toast({ type = 'info', message, onClose, duration = 3000 }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const baseClasses = 'fixed bottom-4 right-4 p-4 rounded-lg shadow-lg flex items-center gap-2 animate-slide-up max-w-md';
  
  const typeClasses = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    info: 'bg-blue-500 text-white',
    warning: 'bg-yellow-500 text-white',
  };

  const icons = {
    success: <CheckCircle size={20} />,
    error: <XCircle size={20} />,
    info: <Info size={20} />,
    warning: <AlertCircle size={20} />,
  };

  return (
    <div className={`${baseClasses} ${typeClasses[type]}`}>
      {icons[type]}
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}

export function useToast() {
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return {
    toasts,
    showToast,
    removeToast,
    success: (msg) => showToast(msg, 'success'),
    error: (msg) => showToast(msg, 'error'),
    info: (msg) => showToast(msg, 'info'),
    warning: (msg) => showToast(msg, 'warning'),
  };
}

export function ToastContainer({ toasts, removeToast }) {
  return (
    <div className="fixed bottom-4 right-4 space-y-2">
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          type={toast.type}
          message={toast.message}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

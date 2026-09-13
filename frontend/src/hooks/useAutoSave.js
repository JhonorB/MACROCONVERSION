import { useState, useEffect, useRef } from 'react';

export const useAutoSave = (saveFunction, delay = 500) => {
  const [status, setStatus] = useState('idle'); // idle, saving, saved, error
  const timeoutRef = useRef(null);

  const triggerSave = (...args) => {
    setStatus('saving');
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      try {
        await saveFunction(...args);
        setStatus('saved');
        setTimeout(() => setStatus('idle'), 2000);
      } catch (error) {
        setStatus('error');
      }
    }, delay);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { status, triggerSave };
};

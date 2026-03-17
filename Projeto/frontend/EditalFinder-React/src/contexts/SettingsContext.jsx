import { createContext, useState, useEffect, useContext } from 'react';

const SettingsContext = createContext();

export const useSettings = () => useContext(SettingsContext);

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('editalFinderSettings');
    return saved ? JSON.parse(saved) : {
      logoText: 'Edital Finder',
      logoImage: null,
      primaryBlue: '#1E88E5',
      primaryYellow: '#FFC107',
    };
  });

  useEffect(() => {
    localStorage.setItem('editalFinderSettings', JSON.stringify(settings));
    
    // Update CSS variables globally
    document.documentElement.style.setProperty('--primary-blue', settings.primaryBlue);
    document.documentElement.style.setProperty('--primary-yellow', settings.primaryYellow);
  }, [settings]);

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

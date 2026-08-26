if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch((error) => {
      console.warn('[Clínica da Construção Civil] Service worker não registrado:', error);
    });
  });
}

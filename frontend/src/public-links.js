const PUBLIC_ROUTES = {
  '/sobre': '/sobre/',
  '/privacidade': '/privacidade/',
  '/termos': '/termos/',
  '/ajuda': '/ajuda/',
};

function routeFromAnchor(anchor) {
  if (!(anchor instanceof HTMLAnchorElement)) return null;
  const href = anchor.getAttribute('href') || '';
  const hashRoute = href.includes('#') ? href.split('#')[1] : '';
  const normalized = hashRoute.replace(/^\//, '/').replace(/\/$/, '') || '';
  return PUBLIC_ROUTES[normalized] || null;
}

document.addEventListener('click', (event) => {
  const anchor = event.target.closest?.('.landing-footer a');
  const publicUrl = routeFromAnchor(anchor);
  if (!publicUrl) return;

  event.preventDefault();
  event.stopPropagation();
  window.location.assign(publicUrl);
}, true);

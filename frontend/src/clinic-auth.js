import './clinic-billing.css';
import './clinic-billing.js';

function applyClinicAuthIdentity() {
  document.querySelectorAll('.custom-auth-card').forEach((card) => {
    const title = card.querySelector('.custom-auth-header h1');
    if (title?.textContent.trim() === 'Entrar no DomnAI') {
      title.textContent = 'Entrar na Clínica da Construção Civil';
    }

    const ariaTitle = card.getAttribute('aria-labelledby');
    if (ariaTitle === 'auth-title' && title) {
      title.id = 'auth-title';
    }
  });
}

const clinicAuthObserver = new MutationObserver(() => {
  applyClinicAuthIdentity();
});

clinicAuthObserver.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyClinicAuthIdentity, { once: true });
} else {
  applyClinicAuthIdentity();
}

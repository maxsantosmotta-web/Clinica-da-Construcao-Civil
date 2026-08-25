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

async function ensurePersistedAdminLifetimeAccess() {
  if (window.__clinicAdminLifetimeChecked) return;

  for (let attempt = 0; attempt < 40; attempt += 1) {
    const session = window.Clerk?.session;
    if (!session) {
      await new Promise((resolve) => window.setTimeout(resolve, 150));
      continue;
    }

    const token = await session.getToken({ skipCache: attempt > 0 }).catch(() => null);
    if (!token) {
      await new Promise((resolve) => window.setTimeout(resolve, 150));
      continue;
    }

    window.__clinicAdminLifetimeChecked = true;

    try {
      const accessResponse = await fetch('/api/auth/access-mode', {
        headers: { Authorization: `Bearer ${token}` },
        cache: 'no-store',
      });
      const access = await accessResponse.json().catch(() => ({}));
      if (!accessResponse.ok || access.isAdmin !== true) return;

      const statusResponse = await fetch('/api/billing/status', {
        headers: { Authorization: `Bearer ${token}` },
        cache: 'no-store',
      });
      if (!statusResponse.ok) return;

      const status = await statusResponse.json();
      window.__domnaiBillingStatus = status;
      window.dispatchEvent(new CustomEvent('domnai:billing-updated', { detail: status }));
    } catch {
      // Não bloqueia o login caso a sincronização administrativa falhe.
    }
    return;
  }
}

const clinicAuthObserver = new MutationObserver(() => {
  applyClinicAuthIdentity();
  ensurePersistedAdminLifetimeAccess();
});

clinicAuthObserver.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    applyClinicAuthIdentity();
    ensurePersistedAdminLifetimeAccess();
  }, { once: true });
} else {
  applyClinicAuthIdentity();
  ensurePersistedAdminLifetimeAccess();
}

window.addEventListener('pageshow', ensurePersistedAdminLifetimeAccess);

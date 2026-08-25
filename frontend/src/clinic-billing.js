const CLINIC_BILLING = {
  monthly: {
    product: 'premium_monthly',
    price: 'R$ 10,90',
    suffix: '/mês',
    copy: 'Cobrança mensal. Cancele quando quiser.',
    button: 'Assinar plano mensal',
  },
  yearly: {
    product: 'premium_yearly',
    price: 'R$ 99,00',
    suffix: '/ano',
    copy: 'Plano anual promocional com pagamento único por 12 meses.',
    button: 'Assinar plano anual',
  },
};

function clinicBillingWait(delay) {
  return new Promise((resolve) => window.setTimeout(resolve, delay));
}

async function clinicBillingToken() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const session = window.Clerk?.session;
    if (session) {
      const token = await session.getToken({ skipCache: attempt > 0 }).catch(() => null);
      if (token) return token;
    }
    await clinicBillingWait(150);
  }
  throw new Error('Sessão não confirmada. Entre novamente.');
}

async function clinicCheckout(button) {
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = 'Abrindo pagamento...';

  try {
    const token = await clinicBillingToken();
    const response = await fetch('/api/billing/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ product: button.dataset.billingProduct }),
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || payload.message || 'Não foi possível abrir o pagamento.');
    }
    if (!payload.url) throw new Error('Link de pagamento não retornado.');

    window.location.assign(payload.url);
  } catch (error) {
    window.alert(error?.message || 'Não foi possível abrir o pagamento.');
    button.disabled = false;
    button.textContent = originalText;
  }
}

function clinicBillingReturn(event) {
  event?.preventDefault();
  const dashboardButton = [...document.querySelectorAll('.sidebar-navigation button')]
    .find((button) => button.textContent.trim().includes('Dashboard'));
  if (dashboardButton) {
    dashboardButton.click();
    return;
  }
  window.location.hash = '#/';
}

function setClinicBillingPeriod(section, period) {
  const config = CLINIC_BILLING[period] || CLINIC_BILLING.monthly;
  const monthly = section.querySelector('[data-clinic-period="monthly"]');
  const yearly = section.querySelector('[data-clinic-period="yearly"]');
  const price = section.querySelector('[data-clinic-price]');
  const suffix = section.querySelector('[data-clinic-suffix]');
  const copy = section.querySelector('[data-clinic-copy]');
  const action = section.querySelector('[data-billing-product]');

  monthly?.classList.toggle('is-active', period === 'monthly');
  yearly?.classList.toggle('is-active', period === 'yearly');
  if (price) price.textContent = config.price;
  if (suffix) suffix.textContent = config.suffix;
  if (copy) copy.textContent = config.copy;
  if (action) {
    action.dataset.billingProduct = config.product;
    action.textContent = config.button;
  }
}

function renderClinicBilling(section) {
  if (!section || section.dataset.clinicBillingRendered === 'true') return;

  const headerLabel = section.querySelector(':scope > header span')?.textContent?.trim();
  const looksLikeBilling = headerLabel === 'Faturamento'
    || section.querySelector('.billing-page-header, .billing-loading-state, [data-billing-product]');

  if (!looksLikeBilling) return;

  section.dataset.clinicBillingRendered = 'true';
  section.innerHTML = `
    <div class="clinic-billing-page">
      <header class="clinic-billing-header">
        <span>Plano</span>
        <h1>Clínica da Construção Civil</h1>
        <p>Escolha a forma de pagamento e tenha acesso ao treinamento.</p>
      </header>

      <section class="clinic-plan-card">
        <span class="clinic-plan-eyebrow">Acesso completo</span>
        <h2 class="clinic-plan-title">Plano Clínica da Construção Civil</h2>

        <div class="clinic-period-toggle" role="group" aria-label="Período do plano">
          <button type="button" class="is-active" data-clinic-period="monthly">Mensal</button>
          <button type="button" data-clinic-period="yearly">Anual</button>
        </div>

        <p class="clinic-plan-price"><span data-clinic-price>R$ 10,90</span><small data-clinic-suffix>/mês</small></p>
        <p class="clinic-plan-copy" data-clinic-copy>Cobrança mensal. Cancele quando quiser.</p>

        <ul class="clinic-plan-benefits">
          <li>Acesso completo ao treinamento</li>
          <li>Aulas em vídeo, apostilas e materiais complementares</li>
          <li>Conteúdo de elétrica, hidráulica, manutenção e serviços essenciais</li>
          <li>Estude no seu ritmo e consulte o material sempre que precisar</li>
        </ul>

        <button type="button" class="clinic-plan-action" data-billing-product="premium_monthly">Assinar plano mensal</button>
        <p class="clinic-plan-saving" aria-live="polite"></p>
      </section>

      <button type="button" class="clinic-billing-back">Voltar</button>
    </div>
  `;

  section.querySelector('[data-clinic-period="monthly"]')?.addEventListener('click', () => {
    setClinicBillingPeriod(section, 'monthly');
  });
  section.querySelector('[data-clinic-period="yearly"]')?.addEventListener('click', () => {
    setClinicBillingPeriod(section, 'yearly');
  });
  section.querySelector('.clinic-plan-action')?.addEventListener('click', (event) => {
    event.preventDefault();
    clinicCheckout(event.currentTarget);
  });
  section.querySelector('.clinic-billing-back')?.addEventListener('click', clinicBillingReturn);
}

function enforceClinicBilling() {
  document.querySelectorAll('.internal-section').forEach((section) => {
    const isBilling = section.querySelector('.billing-page-header, .billing-loading-state, [data-billing-product]')
      || section.querySelector(':scope > header span')?.textContent?.trim() === 'Faturamento';
    if (!isBilling) return;

    if (section.dataset.clinicBillingRendered === 'true') {
      const legacyContent = section.querySelector('.billing-balance-grid, .billing-current-plan, .billing-plans-grid, .billing-credit-card, .billing-consumption-card');
      if (!legacyContent) return;
      delete section.dataset.clinicBillingRendered;
    }

    renderClinicBilling(section);
  });
}

const clinicBillingObserver = new MutationObserver(() => {
  window.requestAnimationFrame(enforceClinicBilling);
});
clinicBillingObserver.observe(document.documentElement, { childList: true, subtree: true });
window.addEventListener('hashchange', () => window.setTimeout(enforceClinicBilling, 0));
window.setTimeout(enforceClinicBilling, 0);

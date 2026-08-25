function applyClinicLandingIdentity() {
  const landingCard = document.querySelector('.landing-card');
  if (!landingCard) return;

  landingCard.setAttribute('aria-label', 'Acesso à Clínica da Construção Civil');

  const logo = landingCard.querySelector('.official-logo');
  if (logo) {
    logo.alt = 'Clínica da Construção Civil';
  }

  if (!landingCard.querySelector('.clinic-brand-copy')) {
    const brandCopy = document.createElement('div');
    brandCopy.className = 'clinic-brand-copy';
    brandCopy.innerHTML = `
      <div class="clinic-brand-topline">Clínica da</div>
      <h1 class="clinic-brand-title">Construção <span class="clinic-civil">Civil</span></h1>
      <p class="clinic-brand-subtitle">Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.</p>
    `;

    const actions = landingCard.querySelector('.access-actions');
    if (actions) {
      landingCard.insertBefore(brandCopy, actions);
    } else if (logo) {
      logo.insertAdjacentElement('afterend', brandCopy);
    }
  }

  const primaryButton = landingCard.querySelector('.primary-button');
  const secondaryButton = landingCard.querySelector('.secondary-button');

  [primaryButton, secondaryButton].forEach((button) => {
    if (!button || button.querySelector('.clinic-button-arrow')) return;
    const arrow = document.createElement('span');
    arrow.className = 'clinic-button-arrow';
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '→';
    button.appendChild(arrow);
  });
}

const clinicLandingObserver = new MutationObserver(() => {
  applyClinicLandingIdentity();
});

clinicLandingObserver.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyClinicLandingIdentity, { once: true });
} else {
  applyClinicLandingIdentity();
}

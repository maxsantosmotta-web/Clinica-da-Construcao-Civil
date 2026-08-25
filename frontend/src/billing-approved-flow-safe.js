import './billing-approved-flow-safe.css';

function planAccessReady() {
  if (window.__clinicAdminAccess === true) return true;
  const status = window.__domnaiBillingStatus;
  return Boolean(status?.profileCompleted && status?.plan && !['unselected', 'free_demo'].includes(status.plan));
}

function findBillingButton() {
  return [...document.querySelectorAll('.sidebar-navigation button')].find((button) => button.textContent.trim().includes('Faturamento'));
}

function keepBillingSelected() {
  if (planAccessReady()) return;
  const billingButton = findBillingButton();
  if (billingButton && !billingButton.classList.contains('is-active')) billingButton.click();
}

async function signOutFromPlanFlow(button) {
  if (button) { button.disabled = true; button.textContent = 'Saindo...'; }
  try {
    if (typeof window.domnaiSafeSignOut !== 'function') throw new Error('Sessão não encontrada.');
    await window.domnaiSafeSignOut();
  } catch (error) {
    if (button) { button.disabled = false; button.textContent = 'Sair da conta'; }
    window.alert(error?.message || 'Não foi possível sair da conta.');
  }
}

function decorateBillingSignOutButton() {
  if (window.__clinicAdminAccess === true) return;
  const button = document.querySelector('[data-billing-action="back-to-chat"]');
  if (!button || button.dataset.approvedBillingBack === 'true') return;
  button.dataset.approvedBillingBack = 'true';
  button.textContent = 'Sair da conta';
  button.setAttribute('aria-label', 'Sair da conta');
  button.classList.add('billing-approved-back');
}

function addProfileTopSignOut() {
  if (window.__clinicAdminAccess === true) return;
  const overlay = document.querySelector('.profile-checklist-overlay');
  const header = overlay?.querySelector('.profile-checklist-card > header');
  if (!overlay || !header || header.querySelector('.profile-checklist-top-cancel')) return;
  const logoutButton = document.createElement('button');
  logoutButton.type = 'button';
  logoutButton.className = 'profile-checklist-top-cancel';
  logoutButton.textContent = 'Sair da conta';
  logoutButton.setAttribute('aria-label', 'Sair da conta');
  logoutButton.addEventListener('click', () => signOutFromPlanFlow(logoutButton));
  header.appendChild(logoutButton);
}

function removeProfileLowerBack() {
  if (window.__clinicAdminAccess === true) return;
  document.querySelector('.profile-checklist-overlay .profile-checklist-cancel')?.remove();
}

function applyApprovedDetails() {
  if (window.__clinicAdminAccess === true) return;
  decorateBillingSignOutButton();
  addProfileTopSignOut();
  removeProfileLowerBack();
  keepBillingSelected();
}

const scheduledDelays = [0, 60, 160, 350, 700, 1200, 2200, 4000, 7000];
function scheduleApprovedDetails() { scheduledDelays.forEach((delay) => window.setTimeout(applyApprovedDetails, delay)); }

document.addEventListener('click', (event) => {
  if (window.__clinicAdminAccess === true) return;
  const freeButton = event.target.closest?.('[data-billing-action="free"]');
  if (freeButton) scheduleApprovedDetails();
  const billingSignOut = event.target.closest?.('[data-billing-action="back-to-chat"]');
  if (billingSignOut && !planAccessReady()) {
    event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation();
    signOutFromPlanFlow(billingSignOut); return;
  }
  if (planAccessReady()) return;
  const navigationButton = event.target.closest?.('.sidebar-navigation button');
  if (navigationButton && !navigationButton.textContent.trim().includes('Faturamento')) {
    event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation(); keepBillingSelected();
  }
}, true);

window.addEventListener('clinic:admin-access', (event) => {
  if (event.detail?.isAdmin === true) window.__clinicAdminAccess = true;
});
window.addEventListener('domnai:billing-updated', scheduleApprovedDetails);
window.addEventListener('pageshow', scheduleApprovedDetails);
window.addEventListener('hashchange', scheduleApprovedDetails);
scheduleApprovedDetails();

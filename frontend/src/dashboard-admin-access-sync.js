const CLINIC_OWNER_USER_ID = 'user_3IO0iCF2RnRzluAa4NWzKxhjTmJ';
const ADMIN_ENTRY_KEY = 'domnai:admin-requested:v1';

function removeLegacyAdminEntry() {
  document.querySelectorAll('[data-clinic-owner-admin-entry="true"]').forEach((node) => node.remove());
}

function syncClinicOwnerAdminEntry() {
  const clerk = window.Clerk;
  const currentUserId = clerk?.user?.id || clerk?.session?.user?.id || '';
  const navigation = document.querySelector('.sidebar-navigation');

  if (!navigation || currentUserId !== CLINIC_OWNER_USER_ID || window.location.hash.startsWith('#/admin')) {
    removeLegacyAdminEntry();
    return;
  }

  if (navigation.querySelector('[data-domnai-admin-menu="true"]') || navigation.querySelector('[data-clinic-owner-admin-entry="true"]')) {
    return;
  }

  const group = document.createElement('div');
  group.className = 'sidebar-group domnai-user-admin-group';
  group.dataset.clinicOwnerAdminEntry = 'true';

  const title = document.createElement('p');
  title.textContent = 'Admin';

  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'domnai-user-admin-button';
  button.innerHTML = '<span>◇</span> Painel Adm <small>Adm</small>';
  button.addEventListener('click', () => {
    sessionStorage.setItem(ADMIN_ENTRY_KEY, 'true');
    window.location.hash = '/admin';
  });

  group.append(title, button);
  navigation.appendChild(group);
}

function startClinicOwnerAdminSync() {
  syncClinicOwnerAdminEntry();
  window.setInterval(syncClinicOwnerAdminEntry, 300);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startClinicOwnerAdminSync, { once: true });
} else {
  startClinicOwnerAdminSync();
}

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '@clerk/clerk-react';

const ADMIN_ENTRY_KEY = 'domnai:admin-requested:v1';

export default function AdminEntryBridge() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  const [target, setTarget] = useState(null);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) {
      setIsAdmin(false);
      return undefined;
    }

    let cancelled = false;

    (async () => {
      try {
        const token = await getToken();
        const response = await fetch('/api/auth/access-mode', {
          headers: { Authorization: `Bearer ${token}` },
          cache: 'no-store',
        });
        const payload = await response.json().catch(() => ({}));
        if (!cancelled) setIsAdmin(response.ok && payload.isAdmin === true);
      } catch {
        if (!cancelled) setIsAdmin(false);
      }
    })();

    return () => { cancelled = true; };
  }, [getToken, isLoaded, isSignedIn]);

  useEffect(() => {
    if (!isAdmin || window.location.hash.startsWith('#/admin')) {
      setTarget(null);
      return undefined;
    }

    const sync = () => {
      const navigation = document.querySelector('.sidebar-navigation');
      setTarget(navigation?.isConnected ? navigation : null);
    };

    sync();
    const interval = window.setInterval(sync, 250);
    return () => window.clearInterval(interval);
  }, [isAdmin]);

  if (!isAdmin || !target) return null;
  if (target.querySelector('[data-domnai-admin-menu="true"]')) return null;

  return createPortal(
    <div className="sidebar-group domnai-user-admin-group" data-domnai-admin-menu="true">
      <p>Admin</p>
      <button
        type="button"
        className="domnai-user-admin-button"
        onClick={() => {
          sessionStorage.setItem(ADMIN_ENTRY_KEY, 'true');
          window.location.hash = '/admin';
        }}
      >
        <span>◇</span>
        Painel Adm
        <small>Adm</small>
      </button>
    </div>,
    target,
  );
}
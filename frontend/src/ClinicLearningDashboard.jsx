import React, { useEffect, useMemo, useState } from 'react';
import { useAuth, useClerk, useUser } from '@clerk/clerk-react';
import CLINIC_LOGO from './assets/clinic-logo-data.js';
import './clinic-learning-dashboard.css';

const lessonTitles = [
  'Grandezas elétricas e conceito atômico',
  'Diferença de corrente contínua e alternada',
  'Cálculos básicos da elétrica (triângulo da tensão e da potência)',
  'Condutores elétricos: tipos (barramento, cabo e fio) e padrão de cores dos cabos',
  'Emendas elétricas (fio a fio) e isolantes elétricos',
];

const lessons = Array.from({ length: 39 }, (_, index) => ({
  id: index + 1,
  title: lessonTitles[index] || `Aula ${String(index + 1).padStart(2, '0')}`,
  module: index < 20 ? 'Elétrica' : 'Hidráulica',
  url: index === 0 ? 'https://drive.google.com/file/d/1UCl-EffvwcnUtoqCcGgqJz1k6s-FwZk7/preview' : '',
  description: lessonTitles[index] ? 'Aula prática do treinamento Clínica da Construção Civil.' : 'Conteúdo em preparação.',
}));

const materials = [
  { id: 'pdf-1', title: 'Apostila do curso', type: 'PDF', url: '' },
  { id: 'pdf-2', title: 'Material complementar', type: 'PDF', url: '' },
  { id: 'drive-1', title: 'Pasta de materiais no Drive', type: 'Google Drive', url: '' },
];

const emptyProfile = {
  fullName: '', phone: '', cpf: '', birthDate: '', zipCode: '', street: '', number: '',
  complement: '', lot: '', block: '', building: '', apartment: '', neighborhood: '', city: '', state: '',
};

if (!window.__clinicBillingCycleTrackerInstalled) {
  window.__clinicBillingCycleTrackerInstalled = true;
  document.addEventListener('click', (event) => {
    const target = event.target?.closest?.('button, [role="button"], label');
    if (!target) return;
    const text = String(target.textContent || '').trim().toLowerCase();
    if (text === 'mensal' || text.includes('plano mensal') || text.includes('assinar plano mensal')) localStorage.setItem('clinic:selected-plan-cycle', 'monthly');
    if (text === 'anual' || text.includes('plano anual') || text.includes('assinar plano anual')) localStorage.setItem('clinic:selected-plan-cycle', 'yearly');
  }, true);
}

function ProgressRing({ value }) {
  return <div className="clinic-progress-ring" style={{ '--progress': `${value * 3.6}deg` }}><span>{value}%</span></div>;
}

function ProfileField({ label, value, onChange, type = 'text', required = false }) {
  return <label className="clinic-profile-field"><span>{label}</span><input type={type} value={value || ''} required={required} onChange={(e) => onChange(e.target.value)} /></label>;
}

export default function ClinicLearningDashboard() {
  const { getToken } = useAuth();
  const { signOut } = useClerk();
  const { user } = useUser();
  const [section, setSection] = useState('inicio');
  const [moduleFilter, setModuleFilter] = useState('Todos');
  const [completed, setCompleted] = useState(() => new Set());
  const [playingLessonId, setPlayingLessonId] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [billingStatus, setBillingStatus] = useState(() => window.__domnaiBillingStatus || null);
  const [billingLoading, setBillingLoading] = useState(false);
  const [profile, setProfile] = useState(emptyProfile);
  const [profileLoaded, setProfileLoaded] = useState(false);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMessage, setProfileMessage] = useState('');
  const [hasAvatar, setHasAvatar] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [showMoreAddress, setShowMoreAddress] = useState(false);

  const visibleLessons = useMemo(() => moduleFilter === 'Todos' ? lessons : lessons.filter((lesson) => lesson.module === moduleFilter), [moduleFilter]);
  const progress = Math.round((completed.size / lessons.length) * 100);
  const isAdmin = window.__clinicAdminAccess === true;
  const storedCycle = localStorage.getItem('clinic:selected-plan-cycle');
  const effectiveCycle = billingStatus?.billingCycle || storedCycle;
  const planCycleLabel = effectiveCycle === 'yearly' ? 'Anual' : effectiveCycle === 'monthly' ? 'Mensal' : 'Plano ativo';
  const renewalLabel = billingStatus?.currentPeriodEnd ? new Date(billingStatus.currentPeriodEnd).toLocaleDateString('pt-BR') : null;

  useEffect(() => {
    let cancelled = false;
    async function loadBilling() {
      try {
        const token = await getToken();
        if (!token) return;
        const response = await fetch('/api/billing/status', { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
        if (!response.ok) return;
        const payload = await response.json();
        if (!cancelled) {
          window.__domnaiBillingStatus = payload;
          if (payload.billingCycle) localStorage.setItem('clinic:selected-plan-cycle', payload.billingCycle);
          setBillingStatus(payload);
        }
      } catch {}
    }
    loadBilling();
    return () => { cancelled = true; };
  }, [getToken]);

  async function authorizedFetch(url, options = {}) {
    const token = await getToken();
    return fetch(url, { ...options, headers: { ...(options.headers || {}), Authorization: `Bearer ${token}` } });
  }

  async function loadProfile() {
    setProfileMessage('');
    try {
      const response = await authorizedFetch('/api/profile', { cache: 'no-store' });
      if (!response.ok) throw new Error('Não foi possível carregar seu perfil.');
      const payload = await response.json();
      setProfile({ ...emptyProfile, ...(payload.profile || {}) });
      setHasAvatar(Boolean(payload.hasAvatar));
      setProfileLoaded(true);
      if (payload.hasAvatar) {
        const avatarResponse = await authorizedFetch('/api/profile/avatar', { cache: 'no-store' });
        if (avatarResponse.ok) {
          const blob = await avatarResponse.blob();
          setAvatarUrl((old) => { if (old) URL.revokeObjectURL(old); return URL.createObjectURL(blob); });
        }
      }
    } catch (error) {
      setProfileMessage(error.message || 'Não foi possível carregar seu perfil.');
      setProfileLoaded(true);
    }
  }

  useEffect(() => {
    if (section === 'perfil' && !profileLoaded) loadProfile();
  }, [section, profileLoaded]);

  function navigate(next) {
    setSection(next);
    setMobileOpen(false);
  }

  async function openBilling() {
    setMobileOpen(false);
    setBillingLoading(true);
    try {
      const token = await getToken();
      if (token) {
        const response = await fetch('/api/billing/status', { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
        if (response.ok) {
          const latest = await response.json();
          window.__domnaiBillingStatus = latest;
          if (latest.billingCycle) localStorage.setItem('clinic:selected-plan-cycle', latest.billingCycle);
          setBillingStatus(latest);
        }
      }
    } catch {} finally {
      setBillingLoading(false);
      setSection('faturamento');
    }
  }

  function toggleLesson(id) {
    setCompleted((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  function updateProfile(key, value) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  async function saveProfile(event) {
    event.preventDefault();
    setProfileSaving(true);
    setProfileMessage('');
    try {
      const response = await authorizedFetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: profile.fullName, phone: profile.phone, cpf: profile.cpf, birth_date: profile.birthDate,
          zip_code: profile.zipCode, street: profile.street, number: profile.number, complement: profile.complement,
          lot: profile.lot, block: profile.block, building: profile.building, apartment: profile.apartment,
          neighborhood: profile.neighborhood, city: profile.city, state: profile.state,
        }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível salvar as alterações.');
      setProfile({ ...emptyProfile, ...(payload.profile || profile) });
      setProfileMessage('Alterações salvas com sucesso.');
    } catch (error) {
      setProfileMessage(error.message || 'Não foi possível salvar as alterações.');
    } finally {
      setProfileSaving(false);
    }
  }

  async function uploadAvatar(file) {
    if (!file) return;
    setProfileMessage('');
    try {
      const form = new FormData();
      form.append('file', file);
      const response = await authorizedFetch('/api/profile/avatar', { method: 'POST', body: form });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível alterar a foto.');
      setHasAvatar(true);
      setProfileLoaded(false);
      await loadProfile();
    } catch (error) {
      setProfileMessage(error.message || 'Não foi possível alterar a foto.');
    }
  }

  async function removeAvatar() {
    try {
      const response = await authorizedFetch('/api/profile/avatar', { method: 'DELETE' });
      if (!response.ok && response.status !== 204) throw new Error('Não foi possível remover a foto.');
      if (avatarUrl) URL.revokeObjectURL(avatarUrl);
      setAvatarUrl('');
      setHasAvatar(false);
    } catch (error) {
      setProfileMessage(error.message || 'Não foi possível remover a foto.');
    }
  }

  const email = user?.primaryEmailAddress?.emailAddress || '';
  const initials = (profile.fullName || user?.fullName || email || 'U').trim().charAt(0).toUpperCase();

  return (
    <main className="clinic-course-shell">
      <button type="button" className="clinic-mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Abrir menu">☰</button>
      {mobileOpen ? <button type="button" className="clinic-sidebar-backdrop" onClick={() => setMobileOpen(false)} aria-label="Fechar menu" /> : null}

      <aside className={`clinic-course-sidebar${mobileOpen ? ' is-open' : ''}`}>
        <div className="clinic-course-brand">
          <img src={CLINIC_LOGO} alt="Clínica da Construção Civil" />
          <button type="button" className="clinic-sidebar-close" onClick={() => setMobileOpen(false)}>×</button>
        </div>
        <nav className="sidebar-navigation clinic-course-navigation" aria-label="Área do aluno">
          <button type="button" className={section === 'inicio' ? 'is-active' : ''} onClick={() => navigate('inicio')}><span>⌂</span> Início</button>
          <button type="button" className={section === 'aulas' ? 'is-active' : ''} onClick={() => navigate('aulas')}><span>▶</span> Aulas</button>
          <button type="button" className={section === 'materiais' ? 'is-active' : ''} onClick={() => navigate('materiais')}><span>▤</span> Materiais</button>
          <button type="button" className={section === 'progresso' ? 'is-active' : ''} onClick={() => navigate('progresso')}><span>✓</span> Meu Progresso</button>
          <div className="clinic-nav-separator" />
          <button type="button" className={section === 'faturamento' ? 'is-active' : ''} onClick={openBilling} disabled={billingLoading}><span>◈</span> {billingLoading ? 'Carregando...' : 'Faturamento'}</button>
        </nav>
        <button type="button" className={`clinic-course-account clinic-account-button${section === 'perfil' ? ' is-active' : ''}`} onClick={() => navigate('perfil')}>
          <span className="clinic-account-avatar">{avatarUrl ? <img src={avatarUrl} alt="Foto do perfil" /> : initials}</span>
          <span><strong>Minha conta</strong><small>Perfil e acesso</small></span>
        </button>
      </aside>

      <section className="clinic-course-main">
        {section === 'inicio' ? <><header className="clinic-course-header"><span>Área do aluno</span><h1>Clínica da Construção Civil</h1><p>Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.</p></header><div className="clinic-dashboard-grid"><article className="clinic-hero-card"><div><span>Treinamento prático</span><h2>39 videoaulas organizadas para você avançar no seu ritmo.</h2><p>Os vídeos e materiais serão conectados por link sem alterar a estrutura do curso.</p><button type="button" onClick={() => navigate('aulas')}>Ver aulas</button></div><ProgressRing value={progress} /></article><article className="clinic-stat-card"><strong>39</strong><span>Videoaulas</span><small>Elétrica + Hidráulica</small></article><article className="clinic-stat-card"><strong>{completed.size}</strong><span>Aulas concluídas</span><small>Progresso salvo nesta sessão</small></article><article className="clinic-stat-card"><strong>{materials.length}</strong><span>Materiais</span><small>PDFs e links externos</small></article></div></> : null}

        {section === 'aulas' ? <><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><div className="clinic-filter-row">{['Todos', 'Elétrica', 'Hidráulica'].map((item) => <button key={item} type="button" className={moduleFilter === item ? 'is-active' : ''} onClick={() => setModuleFilter(item)}>{item}</button>)}</div><div className="clinic-lessons-grid">{visibleLessons.map((lesson) => <article className={`clinic-lesson-card${completed.has(lesson.id) ? ' is-complete' : ''}`} key={lesson.id}>{playingLessonId === lesson.id && lesson.url ? <div className="clinic-video-placeholder clinic-lesson-player"><iframe src={lesson.url} title={`Aula ${lesson.id}: ${lesson.title}`} allow="autoplay; fullscreen" allowFullScreen /></div> : <button type="button" className="clinic-video-placeholder clinic-lesson-cover" disabled={!lesson.url} onClick={() => lesson.url && setPlayingLessonId(lesson.id)} aria-label={lesson.url ? `Assistir ${lesson.title}` : `${lesson.title} em preparação`}><img src={CLINIC_LOGO} alt="" aria-hidden="true" /><span className="clinic-lesson-module-badge">{lesson.module}</span><span className="clinic-cover-play" aria-hidden="true">▶</span></button>}<div className="clinic-lesson-copy"><span>{lesson.module}</span><h2>{lesson.id}. {lesson.title}</h2><p>{lesson.description}</p></div><div className="clinic-lesson-actions"><button type="button" disabled={!lesson.url} onClick={() => lesson.url && setPlayingLessonId(lesson.id)}>{lesson.url ? 'Assistir aula' : 'Em preparação'}</button><label><input type="checkbox" checked={completed.has(lesson.id)} onChange={() => toggleLesson(lesson.id)} /> Concluída</label></div></article>)}</div></> : null}

        {section === 'materiais' ? <><header className="clinic-course-header"><span>Materiais complementares</span><h1>PDFs, apostilas e links</h1><p>Área preparada para arquivos PDF, materiais de apoio e pastas do Google Drive.</p></header><div className="clinic-materials-grid">{materials.map((item) => <article className="clinic-material-card" key={item.id}><span className="clinic-material-type">{item.type}</span><div><h2>{item.title}</h2><p>{item.url ? 'Material disponível para visualização.' : 'Material aguardando cadastro do link.'}</p></div><button type="button" disabled={!item.url}>{item.url ? 'Abrir material' : 'Em preparação'}</button></article>)}</div></> : null}

        {section === 'progresso' ? <><header className="clinic-course-header"><span>Meu Progresso</span><h1>Acompanhe sua evolução</h1><p>Veja quantas aulas já foram concluídas e quanto falta para finalizar o treinamento.</p></header><section className="clinic-progress-card"><ProgressRing value={progress} /><div><h2>{completed.size} de 39 aulas concluídas</h2><p>Marque cada aula como concluída para acompanhar sua evolução.</p><div className="clinic-progress-bar"><span style={{ width: `${progress}%` }} /></div></div></section></> : null}

        {section === 'faturamento' ? <><header className="clinic-course-header"><span>Faturamento</span><h1>Seu plano</h1><p>Consulte aqui a modalidade do seu acesso.</p></header><section className="clinic-progress-card"><div className="clinic-material-type">{isAdmin ? 'ADMIN' : 'PLANO ATIVO'}</div><div><h2>{isAdmin ? 'Acesso administrativo vitalício' : `Plano ${planCycleLabel}`}</h2><p>{isAdmin ? 'Seu perfil possui acesso permanente à Clínica da Construção Civil.' : `Sua assinatura é ${planCycleLabel.toLowerCase()}.`}</p>{renewalLabel && !isAdmin ? <p>Próxima renovação/período: {renewalLabel}</p> : null}<button type="button" onClick={() => navigate('inicio')}>Voltar ao início</button></div></section></> : null}

        {section === 'perfil' ? <><header className="clinic-course-header"><span>Minha conta</span><h1>Perfil e acesso</h1><p>Consulte e atualize seus dados cadastrados na Clínica da Construção Civil.</p></header>{!profileLoaded ? <div className="clinic-profile-loading">Carregando perfil...</div> : <form className="clinic-profile-page" onSubmit={saveProfile}><section className="clinic-profile-card clinic-profile-summary"><div className="clinic-profile-photo">{avatarUrl ? <img src={avatarUrl} alt="Foto do perfil" /> : initials}</div><div className="clinic-photo-actions"><label className="clinic-link-button">Alterar foto<input type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={(e) => uploadAvatar(e.target.files?.[0])} /></label>{hasAvatar ? <button type="button" className="clinic-link-button secondary" onClick={removeAvatar}>Remover</button> : null}</div><div><h2>{profile.fullName || user?.fullName || 'Usuário'}</h2><p>{email}</p><small>JPG, PNG ou WEBP · até 5 MB</small></div><span className="clinic-profile-status">Cadastro completo</span></section><section className="clinic-profile-card"><h2>Dados pessoais</h2><p>Informações do titular da conta.</p><div className="clinic-profile-grid"><ProfileField label="Nome completo" value={profile.fullName} onChange={(v) => updateProfile('fullName', v)} required /><ProfileField label="Telefone" value={profile.phone} onChange={(v) => updateProfile('phone', v)} required /><ProfileField label="CPF" value={profile.cpf} onChange={(v) => updateProfile('cpf', v)} required /><ProfileField label="Data de nascimento" type="date" value={profile.birthDate} onChange={(v) => updateProfile('birthDate', v)} required /></div></section><section className="clinic-profile-card"><h2>Endereço completo</h2><p>Informações vinculadas ao seu cadastro.</p><div className="clinic-profile-grid"><ProfileField label="CEP" value={profile.zipCode} onChange={(v) => updateProfile('zipCode', v)} required /><ProfileField label="Rua" value={profile.street} onChange={(v) => updateProfile('street', v)} required /><ProfileField label="Número" value={profile.number} onChange={(v) => updateProfile('number', v)} required /><ProfileField label="Bairro" value={profile.neighborhood} onChange={(v) => updateProfile('neighborhood', v)} required /><ProfileField label="Cidade" value={profile.city} onChange={(v) => updateProfile('city', v)} required /><ProfileField label="Estado" value={profile.state} onChange={(v) => updateProfile('state', v)} required /></div><button type="button" className="clinic-more-address" onClick={() => setShowMoreAddress((v) => !v)}>Mais detalhes do endereço <span>{showMoreAddress ? '−' : '+'}</span></button>{showMoreAddress ? <div className="clinic-profile-grid clinic-extra-address"><ProfileField label="Complemento" value={profile.complement} onChange={(v) => updateProfile('complement', v)} /><ProfileField label="Lote" value={profile.lot} onChange={(v) => updateProfile('lot', v)} /><ProfileField label="Quadra / Bloco" value={profile.block} onChange={(v) => updateProfile('block', v)} /><ProfileField label="Prédio" value={profile.building} onChange={(v) => updateProfile('building', v)} /><ProfileField label="Apartamento" value={profile.apartment} onChange={(v) => updateProfile('apartment', v)} /></div> : null}</section>{profileMessage ? <div className="clinic-profile-message">{profileMessage}</div> : null}<div className="clinic-profile-actions"><button type="submit" disabled={profileSaving}>{profileSaving ? 'Salvando...' : 'Salvar alterações'}</button><button type="button" className="secondary" onClick={() => navigate('inicio')}>Cancelar</button><button type="button" className="danger" onClick={() => signOut({ redirectUrl: '/' })}>Sair da conta</button></div></form>}</> : null}
      </section>
    </main>
  );
}

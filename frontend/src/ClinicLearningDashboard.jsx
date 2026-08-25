import React, { useEffect, useMemo, useState } from 'react';
import { UserButton, useAuth } from '@clerk/clerk-react';
import CLINIC_LOGO from './assets/clinic-logo-data.js';
import './clinic-learning-dashboard.css';

const lessons = Array.from({ length: 39 }, (_, index) => ({
  id: index + 1,
  title: `Aula ${String(index + 1).padStart(2, '0')}`,
  module: index < 20 ? 'Elétrica' : 'Hidráulica',
  url: '',
  description: 'Conteúdo em preparação.',
}));

const materials = [
  { id: 'pdf-1', title: 'Apostila do curso', type: 'PDF', url: '' },
  { id: 'pdf-2', title: 'Material complementar', type: 'PDF', url: '' },
  { id: 'drive-1', title: 'Pasta de materiais no Drive', type: 'Google Drive', url: '' },
];

if (!window.__clinicBillingCycleTrackerInstalled) {
  window.__clinicBillingCycleTrackerInstalled = true;
  document.addEventListener('click', (event) => {
    const target = event.target?.closest?.('button, [role="button"], label');
    if (!target) return;
    const text = String(target.textContent || '').trim().toLowerCase();
    if (text === 'mensal' || text.includes('plano mensal') || text.includes('assinar plano mensal')) {
      localStorage.setItem('clinic:selected-plan-cycle', 'monthly');
    }
    if (text === 'anual' || text.includes('plano anual') || text.includes('assinar plano anual')) {
      localStorage.setItem('clinic:selected-plan-cycle', 'yearly');
    }
  }, true);
}

function ProgressRing({ value }) {
  return <div className="clinic-progress-ring" style={{ '--progress': `${value * 3.6}deg` }}><span>{value}%</span></div>;
}

export default function ClinicLearningDashboard() {
  const { getToken } = useAuth();
  const [section, setSection] = useState('inicio');
  const [moduleFilter, setModuleFilter] = useState('Todos');
  const [completed, setCompleted] = useState(() => new Set());
  const [mobileOpen, setMobileOpen] = useState(false);
  const [billingStatus, setBillingStatus] = useState(() => window.__domnaiBillingStatus || null);
  const [billingLoading, setBillingLoading] = useState(false);

  const visibleLessons = useMemo(() => {
    if (moduleFilter === 'Todos') return lessons;
    return lessons.filter((lesson) => lesson.module === moduleFilter);
  }, [moduleFilter]);

  const progress = Math.round((completed.size / lessons.length) * 100);
  const isAdmin = window.__clinicAdminAccess === true;

  const storedCycle = localStorage.getItem('clinic:selected-plan-cycle');
  const effectiveCycle = billingStatus?.billingCycle || storedCycle;
  const planCycleLabel = effectiveCycle === 'yearly' ? 'Anual' : effectiveCycle === 'monthly' ? 'Mensal' : 'Plano ativo';
  const renewalLabel = billingStatus?.currentPeriodEnd
    ? new Date(billingStatus.currentPeriodEnd).toLocaleDateString('pt-BR')
    : null;

  useEffect(() => {
    let cancelled = false;
    async function loadBilling() {
      try {
        const token = await getToken();
        if (!token) return;
        const response = await fetch('/api/billing/status', {
          headers: { Authorization: `Bearer ${token}` },
          cache: 'no-store',
        });
        if (!response.ok) return;
        const payload = await response.json();
        if (!cancelled) {
          window.__domnaiBillingStatus = payload;
          if (payload.billingCycle) localStorage.setItem('clinic:selected-plan-cycle', payload.billingCycle);
          setBillingStatus(payload);
        }
      } catch {
        // A área do aluno continua utilizável mesmo se a leitura financeira estiver temporariamente indisponível.
      }
    }
    loadBilling();
    return () => { cancelled = true; };
  }, [getToken]);

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
        const response = await fetch('/api/billing/status', {
          headers: { Authorization: `Bearer ${token}` },
          cache: 'no-store',
        });
        if (response.ok) {
          const latest = await response.json();
          window.__domnaiBillingStatus = latest;
          if (latest.billingCycle) localStorage.setItem('clinic:selected-plan-cycle', latest.billingCycle);
          setBillingStatus(latest);
        }
      }
    } catch {
      // Mantém a última informação conhecida sem retirar o usuário da área do aluno.
    } finally {
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

        <div className="clinic-course-account">
          <UserButton afterSignOutUrl="/" />
          <div><strong>Minha conta</strong><small>Perfil e acesso</small></div>
        </div>
      </aside>

      <section className="clinic-course-main">
        {section === 'inicio' ? (
          <>
            <header className="clinic-course-header"><span>Área do aluno</span><h1>Clínica da Construção Civil</h1><p>Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.</p></header>
            <div className="clinic-dashboard-grid">
              <article className="clinic-hero-card"><div><span>Treinamento prático</span><h2>39 videoaulas organizadas para você avançar no seu ritmo.</h2><p>Os vídeos e materiais serão conectados por link sem alterar a estrutura do curso.</p><button type="button" onClick={() => navigate('aulas')}>Ver aulas</button></div><ProgressRing value={progress} /></article>
              <article className="clinic-stat-card"><strong>39</strong><span>Videoaulas</span><small>Elétrica + Hidráulica</small></article>
              <article className="clinic-stat-card"><strong>{completed.size}</strong><span>Aulas concluídas</span><small>Progresso salvo nesta sessão</small></article>
              <article className="clinic-stat-card"><strong>{materials.length}</strong><span>Materiais</span><small>PDFs e links externos</small></article>
            </div>
          </>
        ) : null}

        {section === 'aulas' ? (
          <>
            <header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Estrutura preparada para receber os 39 vídeos.</p></header>
            <div className="clinic-filter-row">{['Todos', 'Elétrica', 'Hidráulica'].map((item) => <button key={item} type="button" className={moduleFilter === item ? 'is-active' : ''} onClick={() => setModuleFilter(item)}>{item}</button>)}</div>
            <div className="clinic-lessons-grid">{visibleLessons.map((lesson) => <article className={`clinic-lesson-card${completed.has(lesson.id) ? ' is-complete' : ''}`} key={lesson.id}><div className="clinic-video-placeholder"><span>▶</span><small>{lesson.url ? 'Vídeo disponível' : 'Link do vídeo pendente'}</small></div><div className="clinic-lesson-copy"><span>{lesson.module}</span><h2>{lesson.title}</h2><p>{lesson.description}</p></div><div className="clinic-lesson-actions"><button type="button" disabled={!lesson.url}>{lesson.url ? 'Assistir aula' : 'Em preparação'}</button><label><input type="checkbox" checked={completed.has(lesson.id)} onChange={() => toggleLesson(lesson.id)} /> Concluída</label></div></article>)}</div>
          </>
        ) : null}

        {section === 'materiais' ? (
          <>
            <header className="clinic-course-header"><span>Materiais complementares</span><h1>PDFs, apostilas e links</h1><p>Área preparada para arquivos PDF, materiais de apoio e pastas do Google Drive.</p></header>
            <div className="clinic-materials-grid">{materials.map((item) => <article className="clinic-material-card" key={item.id}><span className="clinic-material-type">{item.type}</span><div><h2>{item.title}</h2><p>{item.url ? 'Material disponível para visualização.' : 'Material aguardando cadastro do link.'}</p></div><button type="button" disabled={!item.url}>{item.url ? 'Abrir material' : 'Em preparação'}</button></article>)}</div>
          </>
        ) : null}

        {section === 'progresso' ? (
          <>
            <header className="clinic-course-header"><span>Meu Progresso</span><h1>Acompanhe sua evolução</h1><p>Veja quantas aulas já foram concluídas e quanto falta para finalizar o treinamento.</p></header>
            <section className="clinic-progress-card"><ProgressRing value={progress} /><div><h2>{completed.size} de 39 aulas concluídas</h2><p>Marque cada aula como concluída para acompanhar sua evolução.</p><div className="clinic-progress-bar"><span style={{ width: `${progress}%` }} /></div></div></section>
          </>
        ) : null}

        {section === 'faturamento' ? (
          <>
            <header className="clinic-course-header"><span>Faturamento</span><h1>Seu plano</h1><p>Consulte aqui a modalidade do seu acesso.</p></header>
            <section className="clinic-progress-card">
              <div className="clinic-material-type">{isAdmin ? 'ADMIN' : 'PLANO ATIVO'}</div>
              <div>
                <h2>{isAdmin ? 'Acesso administrativo vitalício' : `Plano ${planCycleLabel}`}</h2>
                <p>{isAdmin ? 'Seu perfil possui acesso permanente à Clínica da Construção Civil.' : `Sua assinatura é ${planCycleLabel.toLowerCase()}.`}</p>
                {renewalLabel && !isAdmin ? <p>Próxima renovação/período: {renewalLabel}</p> : null}
                <button type="button" onClick={() => navigate('inicio')}>Voltar ao início</button>
              </div>
            </section>
          </>
        ) : null}
      </section>
    </main>
  );
}

from pathlib import Path

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
CSS = Path('/frontend/src/clinic-learning-dashboard.css')

text = DASHBOARD.read_text(encoding='utf-8')

# Restaurar somente o botão Sair da conta abaixo de Minha conta.
account_block = '''        <button type="button" className={`clinic-course-account clinic-account-button${section === 'perfil' ? ' is-active' : ''}`} onClick={() => navigate('perfil')}>
          <span className="clinic-account-avatar">{avatarUrl ? <img src={avatarUrl} alt="Foto do perfil" /> : initials}</span>
          <span><strong>Minha conta</strong><small>Perfil e acesso</small></span>
        </button>'''
logout_block = account_block + '''
        <button type="button" className="clinic-sidebar-logout" onClick={() => signOut({ redirectUrl: '/' })}>
          <span aria-hidden="true">↪</span> Sair da conta
        </button>'''
if 'className="clinic-sidebar-logout"' not in text:
    if account_block not in text:
        raise RuntimeError('Âncora Minha conta não encontrada; nada foi alterado.')
    text = text.replace(account_block, logout_block, 1)

# Restaurar somente o botão Atualizar no cabeçalho da tela Aulas.
old_lessons_header = '''        {section === 'aulas' ? <><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><div className="clinic-filter-row">'''
new_lessons_header = '''        {section === 'aulas' ? <><div className="clinic-lessons-header-row"><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><button type="button" className="clinic-refresh-button" onClick={() => window.location.reload()} aria-label="Atualizar página"><span aria-hidden="true">↻</span> Atualizar</button></div><div className="clinic-filter-row">'''
if 'className="clinic-refresh-button"' not in text:
    if old_lessons_header not in text:
        raise RuntimeError('Cabeçalho das Aulas não encontrado; nada foi alterado.')
    text = text.replace(old_lessons_header, new_lessons_header, 1)

DASHBOARD.write_text(text, encoding='utf-8')

css = CSS.read_text(encoding='utf-8')
marker = '/* clinic-controls-final-v3 */'
if marker not in css:
    css += '''\n\n/* clinic-controls-final-v3 */
.clinic-sidebar-logout{width:100%;margin-top:10px;border:1px solid rgba(79,225,194,.18);background:rgba(79,225,194,.04);color:#d9fff7;padding:11px 14px;border-radius:12px;text-align:left;font-weight:800;font-size:.9rem;display:flex;gap:9px;align-items:center;cursor:pointer}
.clinic-sidebar-logout:hover{background:rgba(79,225,194,.09);border-color:rgba(79,225,194,.34)}
.clinic-lessons-header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}
.clinic-refresh-button{flex:0 0 auto;border:1px solid rgba(79,225,194,.24);background:#0a1b17;color:#59e3c6;border-radius:12px;padding:10px 14px;font-weight:850;display:flex;align-items:center;gap:7px;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.16)}
.clinic-refresh-button:hover{background:#10251f;border-color:rgba(79,225,194,.42)}
.clinic-refresh-button span{font-size:1.1rem;line-height:1}
@media(max-width:820px){.clinic-lessons-header-row{align-items:flex-start}.clinic-refresh-button{margin-top:0;padding:10px 12px}.clinic-sidebar-logout{margin-top:8px}}
'''
    CSS.write_text(css, encoding='utf-8')

print('Controles finais restaurados: Sair da conta e Atualizar; demais áreas preservadas.')

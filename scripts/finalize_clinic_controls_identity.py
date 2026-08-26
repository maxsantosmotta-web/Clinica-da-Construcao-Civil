from pathlib import Path
import base64
import json
import re

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
CSS = Path('/frontend/src/clinic-learning-dashboard.css')
LOGO_DATA = Path('/frontend/src/assets/clinic-logo-data.js')
PUBLIC = Path('/frontend/public')
MANIFEST = PUBLIC / 'manifest.webmanifest'
INDEX = Path('/frontend/index.html')
SW = PUBLIC / 'sw.js'

# 1) Botão Sair abaixo de Minha conta no menu lateral.
text = DASHBOARD.read_text()
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

# 2) Botão Atualizar no topo direito da tela Aulas.
old_lessons_header = '''        {section === 'aulas' ? <><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><div className="clinic-filter-row">'''
new_lessons_header = '''        {section === 'aulas' ? <><div className="clinic-lessons-header-row"><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><button type="button" className="clinic-refresh-button" onClick={() => window.location.reload()} aria-label="Atualizar página"><span aria-hidden="true">↻</span> Atualizar</button></div><div className="clinic-filter-row">'''
if 'className="clinic-refresh-button"' not in text:
    if old_lessons_header not in text:
        raise RuntimeError('Cabeçalho das Aulas não encontrado; nada foi alterado.')
    text = text.replace(old_lessons_header, new_lessons_header, 1)

DASHBOARD.write_text(text)

css = CSS.read_text()
marker = '/* clinic-controls-final-v1 */'
if marker not in css:
    css += '''\n\n/* clinic-controls-final-v1 */
.clinic-sidebar-logout{width:100%;margin-top:10px;border:1px solid rgba(255,104,114,.28);background:rgba(255,79,92,.06);color:#ff9aa2;padding:11px 14px;border-radius:12px;text-align:left;font-weight:800;font-size:.9rem;display:flex;gap:9px;align-items:center;cursor:pointer}
.clinic-sidebar-logout:hover{background:rgba(255,79,92,.12);border-color:rgba(255,104,114,.42)}
.clinic-lessons-header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}
.clinic-refresh-button{flex:0 0 auto;border:1px solid rgba(79,225,194,.24);background:#0a1b17;color:#59e3c6;border-radius:12px;padding:10px 14px;font-weight:850;display:flex;align-items:center;gap:7px;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.16)}
.clinic-refresh-button:hover{background:#10251f;border-color:rgba(79,225,194,.42)}
.clinic-refresh-button span{font-size:1.1rem;line-height:1}
@media(max-width:820px){.clinic-lessons-header-row{align-items:flex-start}.clinic-refresh-button{margin-top:0;padding:10px 12px}.clinic-sidebar-logout{margin-top:8px}}
'''
CSS.write_text(css)

# 3) Identidade PWA/Android usando a logo oficial já existente no projeto.
# Evita conversão via ImageMagick: publica diretamente o WEBP oficial já usado pela Clínica.
logo_source = LOGO_DATA.read_text()
match = re.search(r'data:image/webp;base64,([^"\\]+)', logo_source)
if not match:
    raise RuntimeError('Logo oficial da Clínica não encontrada em clinic-logo-data.js.')
raw = base64.b64decode(match.group(1))
icon_webp = PUBLIC / 'clinic-app-icon.webp'
icon_webp.write_bytes(raw)

manifest = json.loads(MANIFEST.read_text())
manifest['name'] = 'Clínica da Construção Civil'
manifest['short_name'] = 'Clínica'
manifest['description'] = 'Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.'
manifest['background_color'] = '#031711'
manifest['theme_color'] = '#031711'
manifest['icons'] = [
    {'src': '/clinic-app-icon.webp', 'sizes': 'any', 'type': 'image/webp', 'purpose': 'any'},
    {'src': '/clinic-app-icon.webp', 'sizes': 'any', 'type': 'image/webp', 'purpose': 'maskable'},
]
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

index = INDEX.read_text()
index = re.sub(r'<meta name="application-name" content="[^"]*" />', '<meta name="application-name" content="Clínica da Construção Civil" />', index)
index = re.sub(r'<meta name="apple-mobile-web-app-title" content="[^"]*" />', '<meta name="apple-mobile-web-app-title" content="Clínica" />', index)
index = re.sub(r'<link rel="icon"[^>]*>', '<link rel="icon" type="image/webp" href="/clinic-app-icon.webp" />', index)
index = re.sub(r'<link rel="apple-touch-icon"[^>]*>', '<link rel="apple-touch-icon" href="/clinic-app-icon.webp" />', index)
index = re.sub(r'<title>.*?</title>', '<title>Clínica da Construção Civil</title>', index, count=1)
INDEX.write_text(index)

sw = SW.read_text()
sw = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'clinica-construcao-shell-v3';", sw, count=1)
for old_icon in ("  '/clinic-icon-192.png',\n", "  '/clinic-icon-512.png',\n"):
    sw = sw.replace(old_icon, '')
if "'/clinic-app-icon.webp'" not in sw:
    sw = sw.replace("  '/manifest.webmanifest',", "  '/manifest.webmanifest',\n  '/clinic-app-icon.webp',", 1)
SW.write_text(sw)

print('Clínica finalizada: Sair no menu, Atualizar nas Aulas e identidade PWA/Android atualizada sem ImageMagick.')

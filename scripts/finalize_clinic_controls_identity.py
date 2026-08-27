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

# 1) Preservar controles validados: Sair da conta + Atualizar nas Aulas.
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

old_lessons_header = '''        {section === 'aulas' ? <><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><div className="clinic-filter-row">'''
new_lessons_header = '''        {section === 'aulas' ? <><div className="clinic-lessons-header-row"><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><button type="button" className="clinic-refresh-button" onClick={() => window.location.reload()} aria-label="Atualizar página"><span aria-hidden="true">↻</span> Atualizar</button></div><div className="clinic-filter-row">'''
if 'className="clinic-refresh-button"' not in text:
    if old_lessons_header not in text:
        raise RuntimeError('Cabeçalho das Aulas não encontrado; nada foi alterado.')
    text = text.replace(old_lessons_header, new_lessons_header, 1)

# IMPORTANTE: persistir os controles antes de qualquer releitura do dashboard.
DASHBOARD.write_text(text)

css = CSS.read_text()
controls_marker = '/* clinic-controls-final-v2 */'
if controls_marker not in css:
    css += '''\n\n/* clinic-controls-final-v2 */
.clinic-sidebar-logout{width:100%;margin-top:10px;border:1px solid rgba(255,104,114,.28);background:rgba(255,79,92,.06);color:#ff9aa2;padding:11px 14px;border-radius:12px;text-align:left;font-weight:800;font-size:.9rem;display:flex;gap:9px;align-items:center;cursor:pointer}
.clinic-sidebar-logout:hover{background:rgba(255,79,92,.12);border-color:rgba(255,104,114,.42)}
.clinic-lessons-header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}
.clinic-refresh-button{flex:0 0 auto;border:1px solid rgba(79,225,194,.24);background:#0a1b17;color:#59e3c6;border-radius:12px;padding:10px 14px;font-weight:850;display:flex;align-items:center;gap:7px;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.16)}
.clinic-refresh-button:hover{background:#10251f;border-color:rgba(79,225,194,.42)}
.clinic-refresh-button span{font-size:1.1rem;line-height:1}
@media(max-width:820px){.clinic-lessons-header-row{align-items:flex-start}.clinic-refresh-button{margin-top:0;padding:10px 12px}.clinic-sidebar-logout{margin-top:8px}}
'''
CSS.write_text(css)

# 2) Identidade PWA/Android da Clínica.
logo_source = LOGO_DATA.read_text()
match = re.search(r'data:image/webp;base64,([^"\\]+)', logo_source)
if not match:
    raise RuntimeError('Logo oficial da Clínica não encontrada em clinic-logo-data.js.')
raw = base64.b64decode(match.group(1))
(PUBLIC / 'clinic-app-icon.webp').write_bytes(raw)

manifest = json.loads(MANIFEST.read_text())
manifest['id'] = '/clinica-da-construcao-civil'
manifest['start_url'] = '/#/'
manifest['scope'] = '/'
manifest['name'] = 'Clínica da Construção Civil'
manifest['short_name'] = 'Clínica'
manifest['description'] = 'Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.'
manifest['display'] = 'standalone'
manifest['background_color'] = '#031711'
manifest['theme_color'] = '#031711'
manifest['icons'] = [
    {'src': '/clinic-app-icon.webp?v=4', 'sizes': 'any', 'type': 'image/webp', 'purpose': 'any'},
    {'src': '/clinic-app-icon.webp?v=4', 'sizes': 'any', 'type': 'image/webp', 'purpose': 'maskable'},
]
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

index = INDEX.read_text()
index = re.sub(r'<meta name="application-name" content="[^"]*" />', '<meta name="application-name" content="Clínica da Construção Civil" />', index)
index = re.sub(r'<meta name="apple-mobile-web-app-title" content="[^"]*" />', '<meta name="apple-mobile-web-app-title" content="Clínica" />', index)
index = re.sub(r'<link rel="icon"[^>]*>', '<link rel="icon" type="image/webp" href="/clinic-app-icon.webp?v=4" />', index)
index = re.sub(r'<link rel="apple-touch-icon"[^>]*>', '<link rel="apple-touch-icon" href="/clinic-app-icon.webp?v=4" />', index)
index = re.sub(r'<title>.*?</title>', '<title>Clínica da Construção Civil</title>', index, count=1)
INDEX.write_text(index)

sw = SW.read_text()
sw = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'clinica-construcao-shell-v4';", sw, count=1)
for old_icon in ("  '/clinic-icon-192.png',\n", "  '/clinic-icon-512.png',\n", "  '/clinic-app-icon.webp',\n"):
    sw = sw.replace(old_icon, '')
if "'/clinic-app-icon.webp?v=4'" not in sw:
    sw = sw.replace("  '/manifest.webmanifest',", "  '/manifest.webmanifest',\n  '/clinic-app-icon.webp?v=4',", 1)
SW.write_text(sw)

# 3) Reorganizar os cinco materiais sem tocar na lógica das videoaulas.
text = DASHBOARD.read_text()

old_materials = '''const materials = [
  { id: 'pdf-1', title: 'Apostila do curso', type: 'PDF', url: '' },
  { id: 'pdf-2', title: 'Material complementar', type: 'PDF', url: '' },
  { id: 'drive-1', title: 'Pasta de materiais no Drive', type: 'Google Drive', url: '' },
];'''
new_materials = '''const complementaryMaterials = [
  { id: 'guia-eletrico', title: 'Guia de Comandos Elétricos', type: 'Guia', cover: '', url: '' },
  { id: 'guia-hidraulico', title: 'Guia Hidráulica', type: 'Guia', cover: '/clinic-materials/guia-hidraulica-cover.webp', url: 'https://drive.google.com/file/d/1QvgFJimtLms5iDRMtjWgXJEsC_GKZmoy/view?usp=drivesdk' },
  { id: 'primeiros-clientes', title: 'Como Conseguir os Primeiros Clientes', type: 'Guia prático', cover: '', url: '' },
];

const practicalTools = [
  { id: 'checklist-seguranca', title: 'Checklist de Segurança no Serviço', type: 'Checklist', cover: '', url: '' },
  { id: 'tabela-precos', title: 'Tabela de Preços + Scripts de WhatsApp', type: 'Ferramenta prática', cover: '', url: '' },
];

const materials = [...complementaryMaterials, ...practicalTools];'''
if 'const complementaryMaterials = [' not in text:
    if old_materials not in text:
        raise RuntimeError('Bloco original de materiais não encontrado; nada foi alterado.')
    text = text.replace(old_materials, new_materials, 1)

state_anchor = "  const [showMoreAddress, setShowMoreAddress] = useState(false);"
if 'const [selectedMaterial, setSelectedMaterial]' not in text:
    if state_anchor not in text:
        raise RuntimeError('Âncora de estado do dashboard não encontrada.')
    text = text.replace(state_anchor, state_anchor + "\n  const [selectedMaterial, setSelectedMaterial] = useState(null);", 1)

old_navigate = '''  function navigate(next) {
    setSection(next);
    setMobileOpen(false);
  }'''
new_navigate = '''  function navigate(next) {
    setSelectedMaterial(null);
    setSection(next);
    setMobileOpen(false);
  }

  function openMaterial(item) {
    setSelectedMaterial(item);
    setMobileOpen(false);
  }'''
if 'function openMaterial(item)' not in text:
    if old_navigate not in text:
        raise RuntimeError('Função de navegação não encontrada.')
    text = text.replace(old_navigate, new_navigate, 1)

old_nav_material = '''          <button type="button" className={section === 'materiais' ? 'is-active' : ''} onClick={() => navigate('materiais')}><span>▤</span> Materiais</button>
          <button type="button" className={section === 'progresso' ? 'is-active' : ''} onClick={() => navigate('progresso')}><span>✓</span> Meu Progresso</button>'''
new_nav_material = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
if "navigate('complementares')" not in text:
    if old_nav_material not in text:
        raise RuntimeError('Botões Materiais/Meu Progresso não encontrados.')
    text = text.replace(old_nav_material, new_nav_material, 1)

old_material_section = '''        {section === 'materiais' ? <><header className="clinic-course-header"><span>Materiais complementares</span><h1>PDFs, apostilas e links</h1><p>Área preparada para arquivos PDF, materiais de apoio e pastas do Google Drive.</p></header><div className="clinic-materials-grid">{materials.map((item) => <article className="clinic-material-card" key={item.id}><span className="clinic-material-type">{item.type}</span><div><h2>{item.title}</h2><p>{item.url ? 'Material disponível para visualização.' : 'Material aguardando cadastro do link.'}</p></div><button type="button" disabled={!item.url}>{item.url ? 'Abrir material' : 'Em preparação'}</button></article>)}</div></> : null}'''
new_material_section = '''        {section === 'complementares' ? <>{selectedMaterial ? <section className="clinic-material-reader"><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar aos complementares</button><div className="clinic-material-cover-frame">{selectedMaterial.cover ? <img src={selectedMaterial.cover} alt={`Capa — ${selectedMaterial.title}`} /> : <div className="clinic-material-cover-pending"><span>{selectedMaterial.type}</span><strong>{selectedMaterial.title}</strong><small>Capa pronta para vinculação</small></div>}</div><button type="button" className="clinic-pdf-button" disabled={!selectedMaterial.url} onClick={() => selectedMaterial.url && window.open(selectedMaterial.url, '_blank', 'noopener,noreferrer')}>{selectedMaterial.url ? 'Abrir PDF' : 'PDF pronto para vinculação'}</button></section> : <div className="clinic-materials-grid">{complementaryMaterials.map((item) => <button type="button" className="clinic-material-entry" key={item.id} onClick={() => openMaterial(item)}><span className="clinic-material-type">{item.type}</span><strong>{item.title}</strong><small>Abrir material →</small></button>)}</div>}</> : null}

        {section === 'ferramentas' ? <>{selectedMaterial ? <section className="clinic-material-reader"><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar às ferramentas</button><div className="clinic-material-cover-frame">{selectedMaterial.cover ? <img src={selectedMaterial.cover} alt={`Capa — ${selectedMaterial.title}`} /> : <div className="clinic-material-cover-pending"><span>{selectedMaterial.type}</span><strong>{selectedMaterial.title}</strong><small>Capa pronta para vinculação</small></div>}</div><button type="button" className="clinic-pdf-button" disabled={!selectedMaterial.url} onClick={() => selectedMaterial.url && window.open(selectedMaterial.url, '_blank', 'noopener,noreferrer')}>{selectedMaterial.url ? 'Abrir PDF' : 'PDF pronto para vinculação'}</button></section> : <div className="clinic-materials-grid">{practicalTools.map((item) => <button type="button" className="clinic-material-entry" key={item.id} onClick={() => openMaterial(item)}><span className="clinic-material-type">{item.type}</span><strong>{item.title}</strong><small>Abrir material →</small></button>)}</div>}</> : null}'''
if 'className="clinic-material-reader"' not in text:
    if old_material_section not in text:
        raise RuntimeError('Tela original de Materiais não encontrada.')
    text = text.replace(old_material_section, new_material_section, 1)

old_progress_section = '''        {section === 'progresso' ? <><header className="clinic-course-header"><span>Meu Progresso</span><h1>Acompanhe sua evolução</h1><p>Veja quantas aulas já foram concluídas e quanto falta para finalizar o treinamento.</p></header><section className="clinic-progress-card"><ProgressRing value={progress} /><div><h2>{completed.size} de 39 aulas concluídas</h2><p>Marque cada aula como concluída para acompanhar sua evolução.</p><div className="clinic-progress-bar"><span style={{ width: `${progress}%` }} /></div></div></section></> : null}'''
if old_progress_section in text:
    text = text.replace(old_progress_section, '', 1)

billing_header = '''        {section === 'faturamento' ? <><header className="clinic-course-header"><span>Faturamento</span><h1>Seu plano</h1><p>Consulte aqui a modalidade do seu acesso.</p></header><section className="clinic-progress-card">'''
billing_without_header = '''        {section === 'faturamento' ? <><section className="clinic-progress-card">'''
if billing_header in text:
    text = text.replace(billing_header, billing_without_header, 1)

DASHBOARD.write_text(text)

css = CSS.read_text()
materials_marker = '/* clinic-student-material-sections-v1 */'
if materials_marker not in css:
    css += '''\n\n/* clinic-student-material-sections-v1 */
.clinic-material-entry{min-height:132px;padding:20px;border:1px solid rgba(79,225,194,.16);border-radius:18px;background:linear-gradient(145deg,#0b1d19,#091713);color:#f7fffd;text-align:left;display:flex;flex-direction:column;align-items:flex-start;gap:12px;cursor:pointer;transition:.18s ease}
.clinic-material-entry:hover{transform:translateY(-2px);border-color:rgba(79,225,194,.38);background:#0d211d}
.clinic-material-entry strong{font-size:1.08rem;line-height:1.35}
.clinic-material-entry small{margin-top:auto;color:#55dfc3;font-weight:800}
.clinic-material-reader{max-width:720px;margin-top:28px;display:flex;flex-direction:column;gap:18px;align-items:flex-start}
.clinic-material-back{border:0;background:transparent;color:#56dfc3;font-weight:850;padding:0;cursor:pointer}
.clinic-material-cover-frame{width:min(100%,460px);aspect-ratio:3/4;border:1px solid rgba(79,225,194,.2);border-radius:20px;overflow:hidden;background:#091713;box-shadow:0 20px 55px rgba(0,0,0,.28)}
.clinic-material-cover-frame img{width:100%;height:100%;object-fit:contain;background:#fff;display:block}
.clinic-material-cover-pending{width:100%;height:100%;padding:34px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:flex-end;gap:12px;background:radial-gradient(circle at 70% 18%,rgba(64,219,187,.18),transparent 30%),linear-gradient(145deg,#0d2a23,#06130f)}
.clinic-material-cover-pending span{color:#55dfc3;text-transform:uppercase;font-size:.76rem;font-weight:900;letter-spacing:.12em}
.clinic-material-cover-pending strong{font-size:clamp(1.6rem,4vw,2.4rem);line-height:1.06}
.clinic-material-cover-pending small{color:#8ca79f}
.clinic-pdf-button{width:min(100%,460px);border:0;border-radius:14px;padding:14px 18px;font-weight:900;background:linear-gradient(135deg,#42dfbd,#24a988);color:#06110f;cursor:pointer}
.clinic-pdf-button:disabled{opacity:.48;cursor:not-allowed}
@media(max-width:820px){.clinic-material-reader{width:100%}.clinic-material-cover-frame,.clinic-pdf-button{width:100%}.clinic-material-entry{min-height:116px}}
'''
CSS.write_text(css)

print('Clínica finalizada: cabeçalhos repetidos removidos de Complementares, Ferramentas Práticas e Faturamento; demais áreas preservadas.')
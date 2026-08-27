from pathlib import Path
import re

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
CSS = Path('/frontend/src/clinic-learning-dashboard.css')
text = DASHBOARD.read_text(encoding='utf-8')
base = 'https://' + 'drive.google.com'

# Vincular os cinco materiais já validados.
items = [
    ('guia-eletrico', '1OMuKrGG0IPAMwQdAho83AD4AnRFQT-Cu'),
    ('guia-hidraulico', '1QvgFJimtLms5iDRMtjWgXJEsC_GKZmoy'),
    ('primeiros-clientes', '1CEKbgpp1X1rBWUHpo1DK7NZIeWuwhCJ9'),
    ('checklist-seguranca', '15-FUwki44zVJJXtMth1ryFeegnLKoci5'),
    ('tabela-precos', '10hNvoQVw2GlLBLkDTLdynF1ni6EACD_j'),
]
for material_id, file_id in items:
    pattern = r"(\{ id: '" + re.escape(material_id) + r"', title: '[^']*', type: '[^']*', cover: ')[^']*(', url: ')[^']*(' \})"
    cover = base + '/thumbnail?id=' + file_id + '&sz=w1200'
    url = base + '/file/d/' + file_id + '/view?usp=drivesdk'
    text, count = re.subn(pattern, lambda m: m.group(1) + cover + m.group(2) + url + m.group(3), text, count=1)
    if count != 1:
        raise RuntimeError('Material não encontrado: ' + material_id)

# Menu final: o antigo Complementares vira Guias; o novo Complementares fica separado.
old_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
new_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Guias</button>
          <button type="button" className={section === 'complementares-drive' ? 'is-active' : ''} onClick={() => navigate('complementares-drive')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
if "navigate('complementares-drive')" not in text:
    if old_nav not in text:
        raise RuntimeError('Navegação validada de Complementares/Ferramentas não encontrada; nada foi alterado.')
    text = text.replace(old_nav, new_nav, 1)

# Capa correta de Complementares: exatamente a arte horizontal aprovada pelo usuário.
cover_import = "import CLINIC_COMPLEMENTARES_COVER from './assets/clinic-complementares-cover-data.js';"
if cover_import not in text:
    import_anchor = "import CLINIC_LOGO from './assets/clinic-logo-data.js';"
    if import_anchor not in text:
        raise RuntimeError('Import da logo da Clínica não encontrado; nada foi alterado.')
    text = text.replace(import_anchor, import_anchor + '\n' + cover_import, 1)

# Guia Elétrico: aplicar classe somente a esse leitor/capa para corrigir a proporção,
# sem modificar os outros Guias nem Ferramentas Práticas.
guide_reader_old = '''{selectedMaterial ? <section className="clinic-material-reader"><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar aos complementares</button><div className="clinic-material-cover-frame">'''
guide_reader_new = '''{selectedMaterial ? <section className={`clinic-material-reader${selectedMaterial?.id === 'guia-eletrico' ? ' clinic-guia-eletrico-reader' : ''}`}><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar aos complementares</button><div className={`clinic-material-cover-frame${selectedMaterial?.id === 'guia-eletrico' ? ' clinic-guia-eletrico-cover' : ''}`}>'''
if 'clinic-guia-eletrico-cover' not in text:
    if guide_reader_old not in text:
        raise RuntimeError('Leitor validado de Guias não encontrado; nada foi alterado.')
    text = text.replace(guide_reader_old, guide_reader_new, 1)

# Tela final do novo Complementares: força uma única estrutura conhecida,
# com a capa correta e acesso direto ao Drive.
drive_url = 'https://drive.google.com/drive/folders/1pIAJrpFP6C_XTCd1i5npUo-b0qPndyXS'
final_section = f'''        {{section === 'complementares-drive' ? <section className="clinic-material-reader clinic-complementares-reader"><div className="clinic-material-cover-frame clinic-complementares-cover"><img src={{CLINIC_COMPLEMENTARES_COVER}} alt="Materiais Complementares — Clínica da Construção Civil" /></div><button type="button" className="clinic-pdf-button clinic-complementares-link" onClick={{() => window.open('{drive_url}', '_blank', 'noopener,noreferrer')}}>Acessar link</button></section> : null}}'''

section_pattern = re.compile(r"\s*\{section === 'complementares-drive' \? <section[^\n]*?</section> : null\}")
if section_pattern.search(text):
    text = section_pattern.sub('\n' + final_section, text, count=1)
else:
    ferramentas_anchor = '''        {section === 'ferramentas' ? <>{selectedMaterial ? <section'''
    if ferramentas_anchor not in text:
        raise RuntimeError('Âncora da tela Ferramentas Práticas não encontrada; nada foi alterado.')
    text = text.replace(ferramentas_anchor, final_section + '\n\n' + ferramentas_anchor, 1)

# Restaurar Sair da conta abaixo de Minha conta, sem alterar os demais itens do menu.
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

# Restaurar Atualizar somente na tela de Aulas.
old_lessons_header = '''        {section === 'aulas' ? <><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><div className="clinic-filter-row">'''
new_lessons_header = '''        {section === 'aulas' ? <><div className="clinic-lessons-header-row"><header className="clinic-course-header"><span>Videoaulas</span><h1>Aulas do treinamento</h1><p>Elétrica e Hidráulica organizadas por aula.</p></header><button type="button" className="clinic-refresh-button" onClick={() => window.location.reload()} aria-label="Atualizar página"><span aria-hidden="true">↻</span> Atualizar</button></div><div className="clinic-filter-row">'''
if 'className="clinic-refresh-button"' not in text:
    if old_lessons_header not in text:
        raise RuntimeError('Cabeçalho das Aulas não encontrado; nada foi alterado.')
    text = text.replace(old_lessons_header, new_lessons_header, 1)

DASHBOARD.write_text(text, encoding='utf-8')

# Estilos finais isolados.
css = CSS.read_text(encoding='utf-8')
marker = '/* clinic-final-controls-and-complementares-v1 */'
base_styles = '''
.clinic-sidebar-logout{width:100%;margin-top:10px;border:1px solid rgba(79,225,194,.18);background:rgba(79,225,194,.04);color:#d9fff7;padding:11px 14px;border-radius:12px;text-align:left;font-weight:800;font-size:.9rem;display:flex;gap:9px;align-items:center;cursor:pointer}
.clinic-sidebar-logout:hover{background:rgba(79,225,194,.09);border-color:rgba(79,225,194,.34)}
.clinic-lessons-header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}
.clinic-refresh-button{flex:0 0 auto;border:1px solid rgba(79,225,194,.24);background:#0a1b17;color:#59e3c6;border-radius:12px;padding:10px 14px;font-weight:850;display:flex;align-items:center;gap:7px;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.16)}
.clinic-refresh-button:hover{background:#10251f;border-color:rgba(79,225,194,.42)}
.clinic-refresh-button span{font-size:1.1rem;line-height:1}
.clinic-complementares-reader{width:100%;max-width:900px}
.clinic-complementares-cover{width:100%;min-height:0;aspect-ratio:3/2;background:transparent}
.clinic-complementares-cover img{width:100%;height:100%;object-fit:cover;background:transparent;display:block}
.clinic-complementares-link{width:100%}
@media(max-width:820px){.clinic-lessons-header-row{align-items:flex-start}.clinic-refresh-button{margin-top:0;padding:10px 12px}.clinic-sidebar-logout{margin-top:8px}.clinic-complementares-reader,.clinic-complementares-cover,.clinic-complementares-link{width:100%}}
'''
if marker not in css:
    css += '\n\n' + marker + base_styles
else:
    css = re.sub(r'\.clinic-complementares-reader\{[^}]*\}', '.clinic-complementares-reader{width:100%;max-width:900px}', css, count=1)
    css = re.sub(r'\.clinic-complementares-cover\{[^}]*\}', '.clinic-complementares-cover{width:100%;min-height:0;aspect-ratio:3/2;background:transparent}', css, count=1)
    css = re.sub(r'\.clinic-complementares-cover img\{[^}]*\}', '.clinic-complementares-cover img{width:100%;height:100%;object-fit:cover;background:transparent;display:block}', css, count=1)
    css = re.sub(r'\.clinic-complementares-link\{[^}]*\}', '.clinic-complementares-link{width:100%}', css, count=1)

guide_marker = '/* clinic-guia-eletrico-proportion-v1 */'
if guide_marker not in css:
    css += '''\n\n/* clinic-guia-eletrico-proportion-v1 */
.clinic-guia-eletrico-reader{width:100%;max-width:720px}
.clinic-guia-eletrico-cover{width:min(100%,460px);min-height:0;aspect-ratio:2/3;background:transparent}
.clinic-guia-eletrico-cover img{width:100%;height:100%;object-fit:cover;background:transparent;display:block}
@media(max-width:820px){.clinic-guia-eletrico-reader,.clinic-guia-eletrico-cover{width:100%}}
'''

CSS.write_text(css, encoding='utf-8')
print('Guias preservados. Complementares usa exatamente a capa aprovada e mantém o link do Drive. Controles preservados.')

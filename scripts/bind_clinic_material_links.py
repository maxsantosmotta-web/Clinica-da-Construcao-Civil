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

# Capa correta de Complementares: usar diretamente o arquivo físico enviado pelo usuário em frontend/src/assets.
cover_import = "import CLINIC_COMPLEMENTARES_COVER from './assets/file_0000000035d8820ebf8712ddf4e37326.png';"
if cover_import not in text:
    import_anchor = "import CLINIC_LOGO from './assets/clinic-logo-data.js';"
    if import_anchor not in text:
        raise RuntimeError('Import da logo da Clínica não encontrado; nada foi alterado.')
    text = re.sub(r"\nimport CLINIC_COMPLEMENTARES_COVER from './assets/[^']+';", '', text, count=1)
    text = text.replace(import_anchor, import_anchor + '\n' + cover_import, 1)

# O painel inicial agora contabiliza os 5 materiais existentes + Complementares.
old_material_stat = '<article className="clinic-stat-card"><strong>{materials.length}</strong><span>Materiais</span><small>PDFs e links externos</small></article>'
new_material_stat = '<article className="clinic-stat-card"><strong>{materials.length + 1}</strong><span>Materiais</span><small>PDFs e links externos</small></article>'
if old_material_stat in text:
    text = text.replace(old_material_stat, new_material_stat, 1)

# Guia Elétrico: aplicar classe somente a esse leitor/capa para corrigir a proporção,
# sem modificar os outros Guias nem Ferramentas Práticas.
guide_reader_old = '''{selectedMaterial ? <section className="clinic-material-reader"><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar aos complementares</button><div className="clinic-material-cover-frame">'''
guide_reader_new = '''{selectedMaterial ? <section className={`clinic-material-reader${selectedMaterial?.id === 'guia-eletrico' ? ' clinic-guia-eletrico-reader' : ''}`}><button type="button" className="clinic-material-back" onClick={() => setSelectedMaterial(null)}>← Voltar aos complementares</button><div className={`clinic-material-cover-frame${selectedMaterial?.id === 'guia-eletrico' ? ' clinic-guia-eletrico-cover' : ''}`}>'''
if 'clinic-guia-eletrico-cover' not in text:
    if guide_reader_old not in text:
        raise RuntimeError('Leitor validado de Guias não encontrado; nada foi alterado.')
    text = text.replace(guide_reader_old, guide_reader_new, 1)

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

# Perfil: data de nascimento digitada em DD/MM/AAAA, sem calendário nativo.
helpers_anchor = '''function ProfileField({ label, value, onChange, type = 'text', required = false }) {
  return <label className="clinic-profile-field"><span>{label}</span><input type={type} value={value || ''} required={required} onChange={(e) => onChange(e.target.value)} /></label>;
}'''
helpers_block = helpers_anchor + '''

function formatBirthDateInput(value) {
  const digits = String(value || '').replace(/\D/g, '').slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

function birthDateForInput(value) {
  const raw = String(value || '').trim();
  const iso = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (iso) return `${iso[3]}/${iso[2]}/${iso[1]}`;
  return formatBirthDateInput(raw);
}

function birthDateToIso(value) {
  const raw = String(value || '').trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const match = raw.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!match) return '';
  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const candidate = new Date(Date.UTC(year, month - 1, day));
  if (candidate.getUTCFullYear() !== year || candidate.getUTCMonth() !== month - 1 || candidate.getUTCDate() !== day) return '';
  return `${match[3]}-${match[2]}-${match[1]}`;
}'''
if 'function formatBirthDateInput(value)' not in text:
    if helpers_anchor not in text:
        raise RuntimeError('Componente ProfileField não encontrado; nada foi alterado.')
    text = text.replace(helpers_anchor, helpers_block, 1)

old_profile_load = '''      setProfile({ ...emptyProfile, ...(payload.profile || {}) });'''
new_profile_load = '''      setProfile({ ...emptyProfile, ...(payload.profile || {}), birthDate: birthDateForInput(payload.profile?.birthDate || '') });'''
if old_profile_load in text:
    text = text.replace(old_profile_load, new_profile_load, 1)

old_fetch_start = '''    try {
      const response = await authorizedFetch('/api/profile', {
        method: 'PUT','''
new_fetch_start = '''    try {
      const birthDateIso = birthDateToIso(profile.birthDate);
      if (!birthDateIso) throw new Error('Informe a data de nascimento no formato DD/MM/AAAA.');
      const response = await authorizedFetch('/api/profile', {
        method: 'PUT','''
if 'const birthDateIso = birthDateToIso(profile.birthDate);' not in text:
    if old_fetch_start not in text:
        raise RuntimeError('Início do salvamento de perfil não encontrado; nada foi alterado.')
    text = text.replace(old_fetch_start, new_fetch_start, 1)

text = text.replace('birth_date: profile.birthDate,', 'birth_date: birthDateIso,', 1)
old_saved_profile = '''      setProfile({ ...emptyProfile, ...(payload.profile || profile) });'''
new_saved_profile = '''      const savedProfile = payload.profile || profile;
      setProfile({ ...emptyProfile, ...savedProfile, birthDate: birthDateForInput(savedProfile.birthDate || profile.birthDate) });'''
if old_saved_profile in text:
    text = text.replace(old_saved_profile, new_saved_profile, 1)

old_birth_field = '''<ProfileField label="Data de nascimento" type="date" value={profile.birthDate} onChange={(v) => updateProfile('birthDate', v)} required />'''
new_birth_field = '''<label className="clinic-profile-field"><span>Data de nascimento</span><input type="text" inputMode="numeric" autoComplete="bday" placeholder="DD/MM/AAAA" maxLength={10} value={profile.birthDate || ''} required onChange={(e) => updateProfile('birthDate', formatBirthDateInput(e.target.value))} /></label>'''
if old_birth_field in text:
    text = text.replace(old_birth_field, new_birth_field, 1)
elif 'placeholder="DD/MM/AAAA"' not in text:
    raise RuntimeError('Campo Data de nascimento não encontrado; nada foi alterado.')

DASHBOARD.write_text(text, encoding='utf-8')

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
print('Painel inicial atualizado para 6 materiais; perfil usa data digitada DD/MM/AAAA; restante preservado.')
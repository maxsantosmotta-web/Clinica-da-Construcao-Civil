from pathlib import Path
import re

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
SW = Path('/frontend/public/sw.js')
text = DASHBOARD.read_text(encoding='utf-8')

# Campo reutilizável com placeholder.
field_pattern = re.compile(
    r"function ProfileField\(\{ label, value, onChange, type = 'text', required = false(?:, placeholder = '', disabled = false)? \}\) \{.*?\n\}",
    re.S,
)
field_replacement = """function ProfileField({ label, value, onChange, type = 'text', required = false, placeholder = '' }) {
  return <label className=\"clinic-profile-field\"><span>{label}</span><input type={type} value={value || ''} required={required} placeholder={placeholder} onChange={(e) => onChange?.(e.target.value)} /></label>;
}

function maskBirthDate(value) {
  const digits = String(value || '').replace(/\\D/g, '').slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}"""
if 'function maskBirthDate(value)' not in text:
    text, count = field_pattern.subn(field_replacement, text, count=1)
    if count != 1:
        raise RuntimeError('ProfileField não encontrado; nada foi alterado.')
else:
    # Remove versão antiga com disabled/e-mail se existir.
    text = re.sub(
        r"function ProfileField\(\{ label, value, onChange, type = 'text', required = false, placeholder = '', disabled = false \}\) \{.*?\n\}",
        "function ProfileField({ label, value, onChange, type = 'text', required = false, placeholder = '' }) {\n  return <label className=\"clinic-profile-field\"><span>{label}</span><input type={type} value={value || ''} required={required} placeholder={placeholder} onChange={(e) => onChange?.(e.target.value)} /></label>;\n}",
        text,
        count=1,
        flags=re.S,
    )

# Carrega o perfil assim que a sessão estiver pronta.
text = text.replace(
    "  useEffect(() => {\n    if (section === 'perfil' && !profileLoaded) loadProfile();\n  }, [section, profileLoaded]);",
    "  useEffect(() => {\n    if (user && !profileLoaded) loadProfile();\n  }, [user, profileLoaded]);",
    1,
)

# Payload final: somente nome, telefone e nascimento.
payload_pattern = re.compile(
    r"body: JSON\.stringify\(\{.*?\}\),",
    re.S,
)
payload = """body: JSON.stringify({
          full_name: profile.fullName,
          phone: profile.phone,
          birth_date: profile.birthDate,
        }),"""
text, payload_count = payload_pattern.subn(payload, text, count=1)
if payload_count != 1:
    raise RuntimeError('Payload do perfil não encontrado; nada foi alterado.')

# Nunca exibir [object Object].
text = text.replace(
    "      if (!response.ok) throw new Error(payload.detail || 'Não foi possível salvar as alterações.');",
    "      if (!response.ok) {\n        const detail = typeof payload.detail === 'string' ? payload.detail : Array.isArray(payload.detail) ? payload.detail.map((item) => item?.msg).filter(Boolean).join(' · ') : '';\n        throw new Error(detail || 'Não foi possível salvar as alterações.');\n      }",
    1,
)

# Nome real no rodapé/menu lateral.
text = text.replace(
    '<span><strong>Minha conta</strong><small>Perfil e acesso</small></span>',
    "<span><strong>{profile.fullName || user?.fullName || 'Minha conta'}</strong><small>Perfil e acesso</small></span>",
    1,
)

# Interface final: foto (já existente no resumo) + nome + telefone + data de nascimento.
start = '<section className="clinic-profile-card"><h2>Dados pessoais</h2>'
end = '{profileMessage ? <div className="clinic-profile-message">'
start_index = text.find(start)
end_index = text.find(end, start_index)
if start_index == -1 or end_index == -1:
    raise RuntimeError('Área de perfil não encontrada; nada foi alterado.')

minimal = '''<section className="clinic-profile-card"><h2>Dados pessoais</h2><p>Informações essenciais da sua conta.</p><div className="clinic-profile-grid"><ProfileField label="Nome completo" value={profile.fullName} onChange={(v) => updateProfile('fullName', v)} required /><ProfileField label="Telefone" value={profile.phone} onChange={(v) => updateProfile('phone', v)} required /><ProfileField label="Data de nascimento" value={profile.birthDate} placeholder="DD/MM/AAAA" onChange={(v) => updateProfile('birthDate', maskBirthDate(v))} required /></div></section>'''
text = text[:start_index] + minimal + text[end_index:]

# Provas antes do build: não pode sobrar CPF, endereço ou campo de e-mail dentro da área editável do perfil.
profile_tail = text[text.find("{section === 'perfil'"):]
for forbidden in ('label="CPF"', '<h2>Endereço completo</h2>', 'label="CEP"', 'label="Rua"', 'label="E-mail"'):
    if forbidden in profile_tail:
        raise RuntimeError(f'Campo proibido ainda presente no perfil final: {forbidden}')

DASHBOARD.write_text(text, encoding='utf-8')

# Força atualização da PWA/TWA para não servir a interface antiga após o deploy.
if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'clinica-construcao-shell-v6';", sw, count=1)
    SW.write_text(sw, encoding='utf-8')

print('Perfil final confirmado: foto, nome, telefone e data de nascimento; cache atualizado para v6.')

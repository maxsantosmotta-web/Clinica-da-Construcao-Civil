from pathlib import Path
import re

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = DASHBOARD.read_text(encoding='utf-8')

# Campo reutilizável: aceita placeholder e disabled sem alterar os demais usos.
old_field = "function ProfileField({ label, value, onChange, type = 'text', required = false }) {\n  return <label className=\"clinic-profile-field\"><span>{label}</span><input type={type} value={value || ''} required={required} onChange={(e) => onChange(e.target.value)} /></label>;\n}"
new_field = "function ProfileField({ label, value, onChange, type = 'text', required = false, placeholder = '', disabled = false }) {\n  return <label className=\"clinic-profile-field\"><span>{label}</span><input type={type} value={value || ''} required={required} placeholder={placeholder} disabled={disabled} onChange={(e) => onChange?.(e.target.value)} /></label>;\n}\n\nfunction maskBirthDate(value) {\n  const digits = String(value || '').replace(/\\D/g, '').slice(0, 8);\n  if (digits.length <= 2) return digits;\n  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;\n  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;\n}"
if old_field in text:
    text = text.replace(old_field, new_field, 1)
elif 'function maskBirthDate(value)' not in text:
    raise RuntimeError('ProfileField esperado não encontrado; nada foi alterado.')

# Carregar o perfil assim que o usuário entra, para o nome aparecer no menu sem exigir abrir o perfil primeiro.
old_effect = "  useEffect(() => {\n    if (section === 'perfil' && !profileLoaded) loadProfile();\n  }, [section, profileLoaded]);"
new_effect = "  useEffect(() => {\n    if (user && !profileLoaded) loadProfile();\n  }, [user, profileLoaded]);"
if old_effect in text:
    text = text.replace(old_effect, new_effect, 1)

# Cadastro mínimo: nome, telefone e nascimento. E-mail vem da autenticação Clerk e não é duplicado na API.
old_body = """        body: JSON.stringify({
          full_name: profile.fullName, phone: profile.phone, cpf: profile.cpf, birth_date: profile.birthDate,
          zip_code: profile.zipCode, street: profile.street, number: profile.number, complement: profile.complement,
          lot: profile.lot, block: profile.block, building: profile.building, apartment: profile.apartment,
          neighborhood: profile.neighborhood, city: profile.city, state: profile.state,
        }),"""
new_body = """        body: JSON.stringify({
          full_name: profile.fullName,
          phone: profile.phone,
          birth_date: profile.birthDate,
        }),"""
if old_body in text:
    text = text.replace(old_body, new_body, 1)
elif 'cpf: profile.cpf' in text:
    raise RuntimeError('Bloco do payload do perfil mudou; nada foi alterado.')

# Mensagem de erro sempre textual, nunca [object Object].
old_error = "      if (!response.ok) throw new Error(payload.detail || 'Não foi possível salvar as alterações.');"
new_error = "      if (!response.ok) {\n        const detail = typeof payload.detail === 'string' ? payload.detail : Array.isArray(payload.detail) ? payload.detail.map((item) => item?.msg).filter(Boolean).join(' · ') : '';\n        throw new Error(detail || 'Não foi possível salvar as alterações.');\n      }"
if old_error in text:
    text = text.replace(old_error, new_error, 1)

# Menu lateral mostra o nome real salvo no perfil.
old_account = '<span><strong>Minha conta</strong><small>Perfil e acesso</small></span>'
new_account = "<span><strong>{profile.fullName || user?.fullName || 'Minha conta'}</strong><small>Perfil e acesso</small></span>"
if old_account in text:
    text = text.replace(old_account, new_account, 1)

# Substituir a área extensa de CPF/endereço por cadastro essencial para produto digital.
start = '<section className="clinic-profile-card"><h2>Dados pessoais</h2>'
end = '{profileMessage ? <div className="clinic-profile-message">'
start_index = text.find(start)
end_index = text.find(end, start_index)
if start_index == -1 or end_index == -1:
    raise RuntimeError('Área de dados pessoais/endereço não encontrada; nada foi alterado.')

minimal = '''<section className="clinic-profile-card"><h2>Dados pessoais</h2><p>Informações essenciais da sua conta.</p><div className="clinic-profile-grid"><ProfileField label="Nome completo" value={profile.fullName} onChange={(v) => updateProfile('fullName', v)} required /><ProfileField label="E-mail" type="email" value={email} disabled /><ProfileField label="Telefone" value={profile.phone} onChange={(v) => updateProfile('phone', v)} required /><ProfileField label="Data de nascimento" value={profile.birthDate} placeholder="DD/MM/AAAA" onChange={(v) => updateProfile('birthDate', maskBirthDate(v))} required /></div></section>'''
text = text[:start_index] + minimal + text[end_index:]

DASHBOARD.write_text(text, encoding='utf-8')
print('Perfil da Clínica simplificado: nome, e-mail, telefone, nascimento e foto; CPF/endereço removidos da interface.')

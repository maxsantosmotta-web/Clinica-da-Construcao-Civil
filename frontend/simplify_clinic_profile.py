from pathlib import Path
import re

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = DASHBOARD.read_text(encoding='utf-8')

# Este script roda depois de bind_clinic_material_links.py. Portanto trabalha
# sobre o estado FINAL intermediário do dashboard e é idempotente.

# Perfil mínimo: somente nome, telefone, nascimento e foto.
text = re.sub(
    r"const emptyProfile = \{.*?\};",
    "const emptyProfile = { fullName: '', phone: '', birthDate: '' };",
    text,
    count=1,
    flags=re.S,
)

# O perfil deve ser carregado assim que houver usuário, para o nome aparecer
# também no menu lateral sem exigir que a pessoa abra primeiro Minha conta.
text = text.replace(
    "  useEffect(() => {\n    if (section === 'perfil' && !profileLoaded) loadProfile();\n  }, [section, profileLoaded]);",
    "  useEffect(() => {\n    if (user && !profileLoaded) loadProfile();\n  }, [user, profileLoaded]);",
    1,
)

# O bind anterior já cria birthDateToIso. Se não existir, interromper o build:
# isso prova que a ordem esperada do pipeline não foi respeitada.
if 'function birthDateToIso(value)' not in text:
    raise RuntimeError('Conversor de data DD/MM/AAAA não encontrado após bind_clinic_material_links.py.')

# Salvar somente os três dados essenciais. Aceita o estado já transformado
# pelo bind (birthDateIso), sem procurar payload antigo por igualdade exata.
payload_pattern = re.compile(
    r"body: JSON\.stringify\(\{\s*full_name: profile\.fullName,.*?\}\),",
    re.S,
)
replacement = "body: JSON.stringify({\n          full_name: profile.fullName,\n          phone: profile.phone,\n          birth_date: birthDateIso,\n        }),"
text, payload_count = payload_pattern.subn(replacement, text, count=1)
if payload_count != 1:
    raise RuntimeError('Payload de salvamento do perfil não localizado no dashboard final intermediário.')

# Exibir mensagens de validação do backend sem [object Object].
text = text.replace(
    "      if (!response.ok) throw new Error(payload.detail || 'Não foi possível salvar as alterações.');",
    "      if (!response.ok) {\n        const detail = typeof payload.detail === 'string' ? payload.detail : Array.isArray(payload.detail) ? payload.detail.map((item) => item?.msg).filter(Boolean).join(' · ') : '';\n        throw new Error(detail || 'Não foi possível salvar as alterações.');\n      }",
    1,
)

# Nome real no menu lateral.
text = text.replace(
    '<span><strong>Minha conta</strong><small>Perfil e acesso</small></span>',
    "<span><strong>{profile.fullName || user?.fullName || 'Minha conta'}</strong><small>Perfil e acesso</small></span>",
    1,
)

# Remover estado exclusivo do endereço, se ainda existir.
text = text.replace("  const [showMoreAddress, setShowMoreAddress] = useState(false);\n", "", 1)

# Substituir Dados pessoais + Endereço por formulário mínimo. A foto permanece
# no cartão-resumo imediatamente anterior.
start = '<section className="clinic-profile-card"><h2>Dados pessoais</h2>'
end = '{profileMessage ? <div className="clinic-profile-message">'
start_index = text.find(start)
end_index = text.find(end, start_index)
if start_index == -1 or end_index == -1:
    raise RuntimeError('Área de Dados pessoais/Endereço não localizada para simplificação.')

minimal = '''<section className="clinic-profile-card"><h2>Dados pessoais</h2><p>Informações essenciais da sua conta.</p><div className="clinic-profile-grid"><ProfileField label="Nome completo" value={profile.fullName} onChange={(v) => updateProfile('fullName', v)} required /><ProfileField label="Telefone" value={profile.phone} onChange={(v) => updateProfile('phone', v)} required /><label className="clinic-profile-field"><span>Data de nascimento</span><input type="text" inputMode="numeric" autoComplete="bday" placeholder="DD/MM/AAAA" maxLength={10} value={profile.birthDate || ''} required onChange={(e) => updateProfile('birthDate', formatBirthDateInput(e.target.value))} /></label></div></section>'''
text = text[:start_index] + minimal + text[end_index:]

# Provas negativas: nenhum campo removido pode continuar no JSX/payload final.
for forbidden in ['label="CPF"', 'label="CEP"', 'label="Rua"', 'profile.cpf', 'profile.zipCode', 'showMoreAddress']:
    if forbidden in text:
        raise RuntimeError(f'Campo removido ainda presente após simplificação: {forbidden}')

DASHBOARD.write_text(text, encoding='utf-8')
print('Perfil final da Clínica: foto, nome, telefone e data de nascimento; sem CPF/endereço.')

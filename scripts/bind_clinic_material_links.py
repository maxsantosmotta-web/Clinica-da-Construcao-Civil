from pathlib import Path
import re

path = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = path.read_text(encoding='utf-8')
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

# O botão atual de materiais vira Guias, preservando integralmente seu conteúdo.
# Em seguida nasce um novo botão Complementares com o mesmo padrão visual do menu.
old_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
new_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Guias</button>
          <button type="button" className={section === 'complementares-drive' ? 'is-active' : ''} onClick={() => navigate('complementares-drive')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
if "navigate('complementares-drive')" not in text:
    if old_nav not in text:
        raise RuntimeError('Navegação validada de Complementares/Ferramentas não encontrada; nada foi alterado.')
    text = text.replace(old_nav, new_nav, 1)

# Estrutura interna inicial do novo Complementares.
# A capa e o link público do Drive serão vinculados depois, sem tocar nos outros blocos.
ferramentas_anchor = '''        {section === 'ferramentas' ? <>{selectedMaterial ? <section className="clinic-material-reader">'''
new_section = '''        {section === 'complementares-drive' ? <section className="clinic-material-reader"><div className="clinic-material-cover-frame"><div className="clinic-material-cover-pending"><span>Materiais complementares</span><strong>Clínica da Construção Civil</strong><small>Capa pronta para vinculação</small></div></div><button type="button" className="clinic-pdf-button" disabled>Acessar link</button></section> : null}\n\n'''
if "section === 'complementares-drive' ? <section" not in text:
    if ferramentas_anchor not in text:
        raise RuntimeError('Âncora da tela Ferramentas Práticas não encontrada; nada foi alterado.')
    text = text.replace(ferramentas_anchor, new_section + ferramentas_anchor, 1)

path.write_text(text, encoding='utf-8')
print('Materiais vinculados; Guias preservado; novo Complementares criado; Ferramentas Práticas preservado.')

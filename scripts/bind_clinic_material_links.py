from pathlib import Path
import re

path = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = path.read_text(encoding='utf-8')
base = 'https://' + 'drive.google.com'
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
path.write_text(text, encoding='utf-8')
print('Materiais vinculados.')

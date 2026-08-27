from pathlib import Path

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = DASHBOARD.read_text(encoding='utf-8')

# Usa diretamente o PNG real já versionado no repositório.
# Evita completamente data URI/base64 e import JS de imagem.
cover_url = 'https://raw.githubusercontent.com/maxsantosmotta-web/Clinica-da-Construcao-Civil/main/frontend/src/assets/file_000000008b74820e866b23c2ff27cc08.png'

text = text.replace("import CLINIC_COMPLEMENTARES_COVER from './assets/clinic-complementares-cover-data.js';\n", '')
text = text.replace('src={CLINIC_COMPLEMENTARES_COVER}', f'src="{cover_url}"')

if cover_url not in text:
    raise RuntimeError('Capa de Complementares não foi aplicada; build interrompido sem alterar outras áreas.')

DASHBOARD.write_text(text, encoding='utf-8')
print('Complementares: capa ligada diretamente ao PNG real do repositório, sem base64.')

from pathlib import Path

path = Path('/frontend/src/main.jsx')
source = path.read_text(encoding='utf-8')

import_marker = "import App from './App';"
admin_import = "import AdminAccessBoundary from './AdminAccessBoundary';"

if admin_import not in source:
    if import_marker not in source:
        raise RuntimeError('Não foi possível localizar a importação principal do App.')
    source = source.replace(import_marker, f"{import_marker}\n{admin_import}", 1)

app_marker = "          <App />"
wrapped_app = "          <AdminAccessBoundary>\n            <App />\n          </AdminAccessBoundary>"

if wrapped_app not in source:
    if app_marker not in source:
        raise RuntimeError('Não foi possível localizar o ponto de montagem do App.')
    source = source.replace(app_marker, wrapped_app, 1)

path.write_text(source, encoding='utf-8')

# Ajuste único e isolado: trocar apenas a imagem usada pelo splash do ADM.
# O mesmo AccessLoading atende a entrada Painel Usuário -> ADM e a saída da conta pelo ADM.
admin_path = Path('/frontend/src/AdminAccessBoundary.jsx')
admin_source = admin_path.read_text(encoding='utf-8')

transparent_import = "import CLINIC_SPLASH_LOGO from './assets/file_000000008b74820e866b23c2ff27cc08.png';"
if transparent_import not in admin_source:
    first_import = "import React, { useEffect, useState } from 'react';"
    if first_import not in admin_source:
        raise RuntimeError('Importação inicial do AdminAccessBoundary não encontrada.')
    admin_source = admin_source.replace(first_import, f"{first_import}\n{transparent_import}", 1)

old_loading_img = '<img src={DOMNAI_LOGO} alt="DomnAI" />'
new_loading_img = '<img src={CLINIC_SPLASH_LOGO} alt="Clínica da Construção Civil" />'

loading_function_start = admin_source.find('function AccessLoading(')
loading_function_end = admin_source.find('function AccessTransitionBlank()', loading_function_start)
if loading_function_start == -1 or loading_function_end == -1:
    raise RuntimeError('Componente AccessLoading não encontrado.')

loading_block = admin_source[loading_function_start:loading_function_end]
if new_loading_img not in loading_block:
    if old_loading_img not in loading_block:
        raise RuntimeError('Imagem atual do splash não encontrada dentro de AccessLoading.')
    loading_block = loading_block.replace(old_loading_img, new_loading_img, 1)
    admin_source = admin_source[:loading_function_start] + loading_block + admin_source[loading_function_end:]

admin_path.write_text(admin_source, encoding='utf-8')
print('Splash ADM: somente o logo quadrado foi substituído pelo logo transparente.')

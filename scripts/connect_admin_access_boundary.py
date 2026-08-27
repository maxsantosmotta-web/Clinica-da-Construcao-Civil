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

# Remoção isolada dos dois splashes do fluxo ADM.
# Preserva validação, navegação e logout; apenas elimina a tela visual de loading.
admin_path = Path('/frontend/src/AdminAccessBoundary.jsx')
admin_source = admin_path.read_text(encoding='utf-8')

admin_source = admin_source.replace(
    'if (isSigningOut) return <AccessLoading showMessage={false} />;',
    'if (isSigningOut) return <AccessTransitionBlank />;',
    1,
)
admin_source = admin_source.replace(
    'if (!isLoaded || !isSignedIn || !userLoaded) return <AccessLoading message="Abrindo Painel Adm..." />;',
    'if (!isLoaded || !isSignedIn || !userLoaded) return <AccessTransitionBlank />;',
    1,
)
admin_source = admin_source.replace(
    'return showAdminLoading\n      ? <AccessLoading message="Abrindo Painel Adm..." />\n      : <AccessTransitionBlank />;',
    'return <AccessTransitionBlank />;',
    1,
)

admin_path.write_text(admin_source, encoding='utf-8')
print('Splashes visuais do fluxo ADM removidos; lógica preservada.')

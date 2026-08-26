from pathlib import Path

path = Path('/frontend/src/App.jsx')
text = path.read_text()

if "import CourseVideoUpload from './CourseVideoUpload';" not in text:
    anchor = "import Dashboard from './Dashboard';"
    if anchor not in text:
        raise RuntimeError('Dashboard import anchor not found for video upload route.')
    text = text.replace(anchor, anchor + "\nimport CourseVideoUpload from './CourseVideoUpload';", 1)

if 'function ProtectedVideoUpload()' not in text:
    anchor = "const institutionalContent = {"
    if anchor not in text:
        raise RuntimeError('Institutional content anchor not found for video upload route.')
    block = """function ProtectedVideoUpload() {\n  const { isLoaded, isSignedIn } = useAuth();\n  if (!isLoaded) return null;\n  return isSignedIn ? <CourseVideoUpload /> : <Navigate to=\"/\" replace />;\n}\n\n"""
    text = text.replace(anchor, block + anchor, 1)

route = '<Route path="/video-aulas" element={<ProtectedVideoUpload />} />'
if route not in text:
    anchor = '<Route path="/sso-callback" element={<AuthenticateWithRedirectCallback />} />'
    if anchor not in text:
        raise RuntimeError('SSO route anchor not found for video upload route.')
    text = text.replace(anchor, anchor + "\n      " + route, 1)

path.write_text(text)

# Conecta a Aula 2 ao MP4 local sem alterar o player ou a Aula 1 já validada.
dashboard_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
dashboard_text = dashboard_path.read_text()

lesson_2_import = "import LESSON_2_VIDEO from './assets/VID-20260824-WA0011.mp4';"
if lesson_2_import not in dashboard_text:
    anchor = "import LESSON_1_VIDEO from './assets/001-Grandezas-eletricas-e-conceito-atomico.mp4';"
    if anchor not in dashboard_text:
        raise RuntimeError('Import da Aula 1 não encontrado para conectar a Aula 2.')
    dashboard_text = dashboard_text.replace(anchor, anchor + "\n" + lesson_2_import, 1)

old_url = "url: index === 0 ? LESSON_1_VIDEO : '',"
new_url = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : '',"
if new_url not in dashboard_text:
    if old_url not in dashboard_text:
        raise RuntimeError('Mapeamento de URL das aulas não encontrado para conectar a Aula 2.')
    dashboard_text = dashboard_text.replace(old_url, new_url, 1)

dashboard_path.write_text(dashboard_text)
print('Rota isolada preservada e Aula 2 conectada ao MP4 local após todos os patches legados.')

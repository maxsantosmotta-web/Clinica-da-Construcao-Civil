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

# Conecta as Aulas 2 e 3 aos MP4s locais sem alterar o player ou a Aula 1 já validada.
dashboard_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
dashboard_text = dashboard_path.read_text()

lesson_1_import = "import LESSON_1_VIDEO from './assets/001-Grandezas-eletricas-e-conceito-atomico.mp4';"
lesson_2_import = "import LESSON_2_VIDEO from './assets/VID-20260824-WA0011.mp4';"
lesson_3_import = "import LESSON_3_VIDEO from './assets/VID-20260824-WA0012.mp4';"

if lesson_1_import not in dashboard_text:
    raise RuntimeError('Import da Aula 1 não encontrado para conectar as próximas aulas.')

if lesson_2_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_1_import, lesson_1_import + "\n" + lesson_2_import, 1)

if lesson_3_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_2_import, lesson_2_import + "\n" + lesson_3_import, 1)

url_aula_1 = "url: index === 0 ? LESSON_1_VIDEO : '',"
url_aulas_1_2 = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : '',"
url_aulas_1_2_3 = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : '',"

if url_aulas_1_2_3 not in dashboard_text:
    if url_aulas_1_2 in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aulas_1_2, url_aulas_1_2_3, 1)
    elif url_aula_1 in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aula_1, url_aulas_1_2_3, 1)
    else:
        raise RuntimeError('Mapeamento de URL das aulas não encontrado para conectar a Aula 3.')

dashboard_path.write_text(dashboard_text)
print('Rota isolada preservada e Aulas 2 e 3 conectadas aos MP4s locais após todos os patches legados.')

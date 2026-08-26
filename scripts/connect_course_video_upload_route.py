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

# Mantém Aulas 1-3 locais e usa Google Drive para a Aula 4.
dashboard_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
dashboard_text = dashboard_path.read_text()

lesson_1_import = "import LESSON_1_VIDEO from './assets/001-Grandezas-eletricas-e-conceito-atomico.mp4';"
lesson_2_import = "import LESSON_2_VIDEO from './assets/VID-20260824-WA0011.mp4';"
lesson_3_import = "import LESSON_3_VIDEO from './assets/VID-20260824-WA0012.mp4';"
lesson_4_import = "import LESSON_4_VIDEO from './assets/Aula_4_comprimida.mp4';"
lesson_4_drive = "https://drive.google.com/file/d/1T3OupIxnquFlhN1XONdHCQ-N4Kz8WNGR/preview"

if lesson_1_import not in dashboard_text:
    raise RuntimeError('Import da Aula 1 não encontrado para conectar as próximas aulas.')

if lesson_2_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_1_import, lesson_1_import + "\n" + lesson_2_import, 1)

if lesson_3_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_2_import, lesson_2_import + "\n" + lesson_3_import, 1)

# O arquivo comprimido da Aula 4 deixa de ser usado pelo player.
if lesson_4_import in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_4_import + "\n", "", 1)
    dashboard_text = dashboard_text.replace(lesson_4_import, "", 1)

url_aula_1 = "url: index === 0 ? LESSON_1_VIDEO : '',"
url_aulas_1_2 = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : '',"
url_aulas_1_2_3 = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : '',"
url_aulas_1_2_3_4_local = "url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : index === 3 ? LESSON_4_VIDEO : '',"
url_aulas_1_2_3_4_drive = f"url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : index === 3 ? '{lesson_4_drive}' : '',"

if url_aulas_1_2_3_4_drive not in dashboard_text:
    if url_aulas_1_2_3_4_local in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aulas_1_2_3_4_local, url_aulas_1_2_3_4_drive, 1)
    elif url_aulas_1_2_3 in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aulas_1_2_3, url_aulas_1_2_3_4_drive, 1)
    elif url_aulas_1_2 in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aulas_1_2, url_aulas_1_2_3_4_drive, 1)
    elif url_aula_1 in dashboard_text:
        dashboard_text = dashboard_text.replace(url_aula_1, url_aulas_1_2_3_4_drive, 1)
    else:
        raise RuntimeError('Mapeamento de URL das aulas não encontrado para conectar a Aula 4 ao Drive.')

# Para links do Drive, usa o player de preview do próprio Drive; MP4s locais continuam no <video> nativo.
video_tag = "<video src={lesson.url} controls autoPlay playsInline onEnded={() => setPlayingLessonId(null)} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', border: 0, background: '#000' }} />"
player_tag = "{lesson.url.includes('drive.google.com') ? <iframe src={lesson.url} title={lesson.title} allow=\"autoplay; encrypted-media\" allowFullScreen style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 0, background: '#000' }} /> : <video src={lesson.url} controls autoPlay playsInline onEnded={() => setPlayingLessonId(null)} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', border: 0, background: '#000' }} />}"

if player_tag not in dashboard_text:
    if video_tag not in dashboard_text:
        raise RuntimeError('Player de video não encontrado para habilitar a Aula 4 via Drive.')
    dashboard_text = dashboard_text.replace(video_tag, player_tag, 1)

dashboard_path.write_text(dashboard_text)
print('Aulas 1-3 locais preservadas e Aula 4 conectada ao Google Drive com preview 16:9.')

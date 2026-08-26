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

# Aulas 1-4 e 7 locais; Aulas 5, 6, 8, 9 e 10 via Google Drive.
dashboard_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
dashboard_text = dashboard_path.read_text()

lesson_1_import = "import LESSON_1_VIDEO from './assets/001-Grandezas-eletricas-e-conceito-atomico.mp4';"
lesson_2_import = "import LESSON_2_VIDEO from './assets/VID-20260824-WA0011.mp4';"
lesson_3_import = "import LESSON_3_VIDEO from './assets/VID-20260824-WA0012.mp4';"
lesson_4_import = "import LESSON_4_VIDEO from './assets/Aula_4_comprimida.mp4';"
lesson_7_import = "import LESSON_7_VIDEO from './assets/VID-20260824-WA0016.mp4';"
lesson_5_drive = "https://drive.google.com/file/d/1T3OupIxnquFlhN1XONdHCQ-N4Kz8WNGR/preview"
lesson_6_drive = "https://drive.google.com/file/d/1JdBBTmP44OidPoS-DHBk-gX7iitADGGP/preview?usp=drivesdk&v=2"
lesson_8_drive = "https://drive.google.com/file/d/1meg3R3NhhWx1kKTlnjMjXVLmOPLN6qgM/preview"
lesson_9_drive = "https://drive.google.com/file/d/1kGJn7VUXhfGxRb4oy1JSzkSqOpJxGRMQ/preview"
lesson_10_drive = "https://drive.google.com/file/d/1xVw7r-tBJOujE35bE4qkyTkjRjMQbLd9/preview"
lesson_6_drive_old = "https://drive.google.com/file/d/1JdBBTmP44OidPoS-DHBk-gX7iitADGGP/preview"

if lesson_1_import not in dashboard_text:
    raise RuntimeError('Import da Aula 1 não encontrado; nada foi alterado.')
if lesson_2_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_1_import, lesson_1_import + "\n" + lesson_2_import, 1)
if lesson_3_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_2_import, lesson_2_import + "\n" + lesson_3_import, 1)
if lesson_4_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_3_import, lesson_3_import + "\n" + lesson_4_import, 1)
if lesson_7_import not in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_4_import, lesson_4_import + "\n" + lesson_7_import, 1)

if lesson_6_drive_old in dashboard_text:
    dashboard_text = dashboard_text.replace(lesson_6_drive_old, lesson_6_drive, 1)

url_1_9 = f"url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : index === 3 ? LESSON_4_VIDEO : index === 4 ? '{lesson_5_drive}' : index === 5 ? '{lesson_6_drive}' : index === 6 ? LESSON_7_VIDEO : index === 7 ? '{lesson_8_drive}' : index === 8 ? '{lesson_9_drive}' : '',"
url_1_10 = f"url: index === 0 ? LESSON_1_VIDEO : index === 1 ? LESSON_2_VIDEO : index === 2 ? LESSON_3_VIDEO : index === 3 ? LESSON_4_VIDEO : index === 4 ? '{lesson_5_drive}' : index === 5 ? '{lesson_6_drive}' : index === 6 ? LESSON_7_VIDEO : index === 7 ? '{lesson_8_drive}' : index === 8 ? '{lesson_9_drive}' : index === 9 ? '{lesson_10_drive}' : '',"

if url_1_10 not in dashboard_text:
    if url_1_9 not in dashboard_text:
        raise RuntimeError('Mapeamento atual das Aulas 1-9 não encontrado; nada foi alterado.')
    dashboard_text = dashboard_text.replace(url_1_9, url_1_10, 1)

# MP4 local mantém 16:9; links do Drive, inclusive Aula 10, usam 16:10.
wrapper_old = "<div className=\"clinic-lesson-player\" style={{ position: 'relative', width: '100%', aspectRatio: '16 / 9', overflow: 'hidden', background: '#000', borderRadius: 18, border: '1px solid rgba(79,225,194,.2)' }}>"
wrapper_new = "<div className=\"clinic-lesson-player\" style={{ position: 'relative', width: '100%', aspectRatio: lesson.url.includes('drive.google.com') ? '16 / 10' : '16 / 9', overflow: 'hidden', background: '#000', borderRadius: 18, border: '1px solid rgba(79,225,194,.2)' }}>"
if wrapper_new not in dashboard_text:
    if wrapper_old not in dashboard_text:
        raise RuntimeError('Bloco visual do player não encontrado; nada foi alterado.')
    dashboard_text = dashboard_text.replace(wrapper_old, wrapper_new, 1)

video_tag = "<video src={lesson.url} controls autoPlay playsInline onEnded={() => setPlayingLessonId(null)} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', border: 0, background: '#000' }} />"
player_tag = "{lesson.url.includes('drive.google.com') ? <iframe src={lesson.url} title={lesson.title} allow=\"autoplay; encrypted-media\" allowFullScreen style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 0, background: '#000' }} /> : <video src={lesson.url} controls autoPlay playsInline onEnded={() => setPlayingLessonId(null)} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', border: 0, background: '#000' }} />}"
if player_tag not in dashboard_text:
    if video_tag not in dashboard_text:
        raise RuntimeError('Player de vídeo não encontrado; nada foi alterado.')
    dashboard_text = dashboard_text.replace(video_tag, player_tag, 1)

dashboard_path.write_text(dashboard_text)
print('Aula 10 conectada ao Google Drive com player 16:10; demais aulas preservadas.')

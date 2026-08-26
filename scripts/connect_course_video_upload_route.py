from pathlib import Path
import re

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

dashboard_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
dashboard_text = dashboard_path.read_text()

lesson_1_import = "import LESSON_1_VIDEO from './assets/001-Grandezas-eletricas-e-conceito-atomico.mp4';"
lesson_2_import = "import LESSON_2_VIDEO from './assets/VID-20260824-WA0011.mp4';"
lesson_3_import = "import LESSON_3_VIDEO from './assets/VID-20260824-WA0012.mp4';"
lesson_4_import = "import LESSON_4_VIDEO from './assets/Aula_4_comprimida.mp4';"
lesson_7_import = "import LESSON_7_VIDEO from './assets/VID-20260824-WA0016.mp4';"
lesson_20_import = "import LESSON_20_VIDEO from './assets/VID-20260824-WA0029.mp4';"
lesson_21_import = "import LESSON_21_VIDEO from './assets/VID-20260824-WA0030.mp4';"
lesson_28_import = "import LESSON_28_VIDEO from './assets/VID-20260824-WA0037.mp4';"
lesson_35_import = "import LESSON_35_VIDEO from './assets/VID-20260824-WA0044.mp4';"

lesson_5_drive = "https://drive.google.com/file/d/1T3OupIxnquFlhN1XONdHCQ-N4Kz8WNGR/preview"
lesson_6_drive = "https://drive.google.com/file/d/1JdBBTmP44OidPoS-DHBk-gX7iitADGGP/preview?usp=drivesdk&v=2"
lesson_8_drive = "https://drive.google.com/file/d/1meg3R3NhhWx1kKTlnjMjXVLmOPLN6qgM/preview"
lesson_9_drive = "https://drive.google.com/file/d/1kGJn7VUXhfGxRb4oy1JSzkSqOpJxGRMQ/preview"
lesson_10_drive = "https://drive.google.com/file/d/1xVw7r-tBJOujE35bE4qkyTkjRjMQbLd9/preview"
lesson_11_drive = "https://drive.google.com/file/d/1fAA8wsN-ln6LzlDaqh2U2t9Ub6bGpsju/preview"
lesson_12_drive = "https://drive.google.com/file/d/1LJXefORuGHTSVUXVkfKfcekhqAo4N3qH/preview"
lesson_13_drive = "https://drive.google.com/file/d/1PKV-sVlxVTmXCx0XbBaZPYcY85hAw-1V/preview"
lesson_14_drive = "https://drive.google.com/file/d/1oNLV0Z6yrJ9DyAMNXeBmvJwH-UzaqMUv/preview"
lesson_15_drive = "https://drive.google.com/file/d/12sAYzLw4x1aMceGQAxzejcNXvdVm5rvw/preview"
lesson_16_drive = "https://drive.google.com/file/d/1gEm-RWbKMoQe_XwWhsFhaZ3CkXuUv2nd/preview"
lesson_17_drive = "https://drive.google.com/file/d/1qnZMrMAL3ufB-gHfY7hn3e9RhEiJh4zq/preview"
lesson_18_drive = "https://drive.google.com/file/d/1Pqf7-f00DyNgmZDyf3cFghYN56traRyV/preview"
lesson_19_drive = "https://drive.google.com/file/d/1sNT3S0UXKSU6h9ZIRo1Wl4FOXpFHGhk6/preview"
lesson_22_drive = "https://drive.google.com/file/d/1_vZDizTE4KNFjPHmi8Fr_RwonvbUwGzD/preview"
lesson_23_drive = "https://drive.google.com/file/d/1w0KSNAly2s_020X_rzdJTtkBjqdq8BqG/preview"
lesson_24_drive = "https://drive.google.com/file/d/1FNRK3cKUvXGfWvXk_HMxCWxrW33OLXnN/preview"
lesson_25_drive = "https://drive.google.com/file/d/11c0koXN2MqPQc8TCW8YgSoeG1zWvpwoe/preview"
lesson_26_drive = "https://drive.google.com/file/d/1T6CrFZkh806OQwSiChEe66jNBLfg9L9U/preview"
lesson_27_drive = "https://drive.google.com/file/d/1DiiXeRls-O436Oj-wZhCF57vmLPPjqWf/preview"
lesson_29_drive = "https://drive.google.com/file/d/1jmJ-wV4oRhelZwVpKTNGNlSapz3LP5GI/preview"
lesson_30_drive = "https://drive.google.com/file/d/1gf59bb3Rcg-LWGJGoYL4V1a1EoEVZL1k/preview"
lesson_31_drive = "https://drive.google.com/file/d/1u-_thvQyVlkNTuyFa5-aQUZVztOzrUq7/preview"
lesson_32_drive = "https://drive.google.com/file/d/1OllmJt5hlWIrEuIjRsMf-keltAjtwfg8/preview"
lesson_33_drive = "https://drive.google.com/file/d/1cl_KZbVt-YZlMBktp-RxObhlvrPRdmnz/preview"
lesson_34_drive = "https://drive.google.com/file/d/1vu27SXvhLL2HfSWZkBY8z9Q8eDgoXq8i/preview"
lesson_36_drive = "https://drive.google.com/file/d/1PQk9GZ6UjocT9zcPq3VbPaN0tS-tDsJl/preview"
lesson_37_drive = "https://drive.google.com/file/d/1mrn-35sbyqjRV9183fBV468hjGn791SD/preview"
lesson_38_drive = "https://drive.google.com/file/d/1fwNhxf-ai0LONxA5Z4vRoxKKGqDMLy4K/preview"

for previous, current in [
    (lesson_1_import, lesson_2_import),
    (lesson_2_import, lesson_3_import),
    (lesson_3_import, lesson_4_import),
    (lesson_4_import, lesson_7_import),
    (lesson_7_import, lesson_20_import),
    (lesson_20_import, lesson_21_import),
    (lesson_21_import, lesson_28_import),
    (lesson_28_import, lesson_35_import),
]:
    if current not in dashboard_text:
        if previous not in dashboard_text:
            raise RuntimeError(f'Import anchor not found: {previous}')
        dashboard_text = dashboard_text.replace(previous, previous + "\n" + current, 1)

mapping = (
    "  url: index === 0 ? LESSON_1_VIDEO "
    ": index === 1 ? LESSON_2_VIDEO "
    ": index === 2 ? LESSON_3_VIDEO "
    ": index === 3 ? LESSON_4_VIDEO "
    f": index === 4 ? '{lesson_5_drive}' "
    f": index === 5 ? '{lesson_6_drive}' "
    ": index === 6 ? LESSON_7_VIDEO "
    f": index === 7 ? '{lesson_8_drive}' "
    f": index === 8 ? '{lesson_9_drive}' "
    f": index === 9 ? '{lesson_10_drive}' "
    f": index === 10 ? '{lesson_11_drive}' "
    f": index === 11 ? '{lesson_12_drive}' "
    f": index === 12 ? '{lesson_13_drive}' "
    f": index === 13 ? '{lesson_14_drive}' "
    f": index === 14 ? '{lesson_15_drive}' "
    f": index === 15 ? '{lesson_16_drive}' "
    f": index === 16 ? '{lesson_17_drive}' "
    f": index === 17 ? '{lesson_18_drive}' "
    f": index === 18 ? '{lesson_19_drive}' "
    ": index === 19 ? LESSON_20_VIDEO "
    ": index === 20 ? LESSON_21_VIDEO "
    f": index === 21 ? '{lesson_22_drive}' "
    f": index === 22 ? '{lesson_23_drive}' "
    f": index === 23 ? '{lesson_24_drive}' "
    f": index === 24 ? '{lesson_25_drive}' "
    f": index === 25 ? '{lesson_26_drive}' "
    f": index === 26 ? '{lesson_27_drive}' "
    ": index === 27 ? LESSON_28_VIDEO "
    f": index === 28 ? '{lesson_29_drive}' "
    f": index === 29 ? '{lesson_30_drive}' "
    f": index === 30 ? '{lesson_31_drive}' "
    f": index === 31 ? '{lesson_32_drive}' "
    f": index === 32 ? '{lesson_33_drive}' "
    f": index === 33 ? '{lesson_34_drive}' "
    ": index === 34 ? LESSON_35_VIDEO "
    f": index === 35 ? '{lesson_36_drive}' "
    f": index === 36 ? '{lesson_37_drive}' "
    f": index === 37 ? '{lesson_38_drive}' : '',"
)

pattern = r"^\s*url:\s*index\s*===\s*0\s*\?.*$"
updated_text, count = re.subn(pattern, mapping, dashboard_text, count=1, flags=re.MULTILINE)
if count != 1:
    raise RuntimeError('Linha de mapeamento das aulas não encontrada; nada foi alterado.')
dashboard_text = updated_text

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
print('Aulas 1-38 mapeadas; Aula 38 no Drive com player 16:10.')

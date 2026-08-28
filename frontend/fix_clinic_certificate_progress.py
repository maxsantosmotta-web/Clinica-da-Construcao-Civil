from pathlib import Path

FILE = Path('/frontend/src/clinic-certificate.js')
text = FILE.read_text(encoding='utf-8')

text = text.replace(
    "const CERTIFICATE_STORAGE_KEY = 'clinic:certificate-completed-at';\n",
    "function certificateStorageKey() {\n  const userId = window.__clinicCourseProgress?.userId || 'local';\n  return `clinic:certificate-completed-at:${userId}`;\n}\n",
    1,
)

read_anchor = "function readProgress() {\n"
if "window.__clinicCourseProgress?.progress" not in text:
    if read_anchor not in text:
        raise RuntimeError('readProgress não encontrado.')
    text = text.replace(
        read_anchor,
        "function readProgress() {\n  const liveProgress = Number(window.__clinicCourseProgress?.progress);\n  if (Number.isFinite(liveProgress)) return liveProgress;\n",
        1,
    )

text = text.replace(
    "  let stored = localStorage.getItem(CERTIFICATE_STORAGE_KEY);\n",
    "  const storageKey = certificateStorageKey();\n  let stored = localStorage.getItem(storageKey);\n",
    1,
)
text = text.replace(
    "    localStorage.setItem(CERTIFICATE_STORAGE_KEY, stored);\n",
    "    localStorage.setItem(storageKey, stored);\n",
    1,
)

text = text.replace("'Certificado ainda bloqueado'", "'Certificado bloqueado'", 1)

listener_anchor = "window.addEventListener('hashchange', scheduleSync);\n"
if "window.addEventListener('clinic-course-progress', scheduleSync);" not in text:
    if listener_anchor not in text:
        raise RuntimeError('Âncora dos listeners do certificado não encontrada.')
    text = text.replace(
        listener_anchor,
        listener_anchor + "window.addEventListener('clinic-course-progress', scheduleSync);\n",
        1,
    )

if "CERTIFICATE_STORAGE_KEY" in text:
    raise RuntimeError('Chave antiga do certificado permaneceu no arquivo.')

FILE.write_text(text, encoding='utf-8')
print('Certificado ligado ao progresso vivo e persistido do aluno; texto de bloqueio simplificado.')

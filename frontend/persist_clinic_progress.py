from pathlib import Path

DASHBOARD = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = DASHBOARD.read_text(encoding='utf-8')

state_anchor = "  const [completed, setCompleted] = useState(() => new Set());\n"
state_replacement = state_anchor + "  const [progressStorageReady, setProgressStorageReady] = useState(false);\n"
if 'progressStorageReady' not in text:
    if state_anchor not in text:
        raise RuntimeError('Estado completed não encontrado; persistência não aplicada.')
    text = text.replace(state_anchor, state_replacement, 1)

progress_anchor = "  const progress = Math.round((completed.size / lessons.length) * 100);\n"
progress_logic = '''  const progress = Math.round((completed.size / lessons.length) * 100);\n\n  useEffect(() => {\n    setProgressStorageReady(false);\n    if (!user?.id) return;\n    const key = `clinic:completed-lessons:${user.id}`;\n    try {\n      const saved = JSON.parse(localStorage.getItem(key) || '[]');\n      const valid = Array.isArray(saved) ? saved.map(Number).filter((id) => Number.isInteger(id) && id >= 1 && id <= lessons.length) : [];\n      setCompleted(new Set(valid));\n    } catch {\n      setCompleted(new Set());\n    }\n    setProgressStorageReady(true);\n  }, [user?.id]);\n\n  useEffect(() => {\n    if (!user?.id || !progressStorageReady) return;\n    const ids = [...completed].map(Number).filter((id) => Number.isInteger(id) && id >= 1 && id <= lessons.length).sort((a, b) => a - b);\n    localStorage.setItem(`clinic:completed-lessons:${user.id}`, JSON.stringify(ids));\n    const detail = { userId: user.id, completed: ids.length, total: lessons.length, progress };\n    window.__clinicCourseProgress = detail;\n    window.dispatchEvent(new CustomEvent('clinic-course-progress', { detail }));\n  }, [user?.id, progressStorageReady, completed, progress]);\n'''
if 'window.__clinicCourseProgress = detail;' not in text:
    if progress_anchor not in text:
        raise RuntimeError('Cálculo de progress não encontrado; persistência não aplicada.')
    text = text.replace(progress_anchor, progress_logic, 1)

DASHBOARD.write_text(text, encoding='utf-8')
print('Persistência do progresso aplicada sem alterar toggleLesson nem o cálculo do contador.')

from pathlib import Path
import re


ATTACHMENT_FIELD = re.compile(
    r'(?P<indent>[ \t]*)attachments:\s*sentAttachments\s*\n'
    r'(?P=indent)\s*\.filter\(\(item\) => item\.libraryId\)\s*\n'
    r'(?P=indent)\s*\.map\(\(item\) => \(\{ library_id: item\.libraryId \}\)\),?\s*\n',
    flags=re.M,
)


def stabilize_frontend() -> None:
    path = Path('/frontend/src/Dashboard.jsx')
    if not path.exists():
        return

    source = path.read_text(encoding='utf-8')
    request_marker = "authorizedFetch('/api/chat/respond', {"
    request_start = source.find(request_marker)
    if request_start < 0:
        raise RuntimeError('Envio /api/chat/respond não localizado no Dashboard final.')

    body_marker = "body: JSON.stringify({"
    body_start = source.find(body_marker, request_start)
    if body_start < 0:
        raise RuntimeError('Payload JSON de /api/chat/respond não localizado.')

    request_end = source.find("      });", body_start)
    if request_end < 0:
        raise RuntimeError('Fim da chamada /api/chat/respond não localizado.')

    body_end = source.find("        }),", body_start, request_end)
    if body_end < 0:
        raise RuntimeError('Fim do payload JSON de /api/chat/respond não localizado.')

    payload = source[body_start:body_end]
    matches = list(ATTACHMENT_FIELD.finditer(payload))
    if not matches:
        raise RuntimeError('Campo de anexos do payload final de /api/chat/respond não localizado.')

    removed = 0
    for match in reversed(matches[1:]):
        absolute_start = body_start + match.start()
        absolute_end = body_start + match.end()
        source = source[:absolute_start] + source[absolute_end:]
        removed += 1

    request_end = source.find("      });", body_start)
    body_end = source.find("        }),", body_start, request_end)
    final_payload = source[body_start:body_end]
    final_matches = list(ATTACHMENT_FIELD.finditer(final_payload))
    if len(final_matches) != 1:
        raise RuntimeError(
            f'O payload final de /api/chat/respond deve conter exatamente um campo de anexos; encontrado(s): {len(final_matches)}.'
        )

    path.write_text(source, encoding='utf-8')
    print(f'Frontend estabilizado: {removed} campo(s) duplicado(s) de anexos removido(s) do payload de /api/chat/respond.')


def connect_clinic_learning_dashboard() -> None:
    path = Path('/frontend/src/Dashboard.jsx')
    if not path.exists():
        return

    source = path.read_text(encoding='utf-8')

    learning_import = "import ClinicLearningDashboard from './ClinicLearningDashboard';"
    if learning_import not in source:
        first_import_end = source.find('\n')
        if first_import_end < 0:
            raise RuntimeError('Não foi possível inserir o import da área de aprendizagem.')
        source = source[:first_import_end + 1] + learning_import + '\n' + source[first_import_end + 1:]

    state_line = '  const [clinicLearningMode, setClinicLearningMode] = useState(true);\n'
    if state_line.strip() not in source:
        function_marker = 'export default function Dashboard() {'
        function_pos = source.find(function_marker)
        if function_pos < 0:
            raise RuntimeError('Função Dashboard não encontrada.')
        insert_pos = function_pos + len(function_marker)
        source = source[:insert_pos] + '\n' + state_line + source[insert_pos:]

    if 'setClinicLearningMode(true);' not in source:
        open_marker = '  function openDashboard() {'
        open_pos = source.find(open_marker)
        if open_pos >= 0:
            insert_pos = open_pos + len(open_marker)
            source = source[:insert_pos] + '\n    setClinicLearningMode(true);' + source[insert_pos:]

    if '<ClinicLearningDashboard' not in source:
        return_pos = source.rfind('\n  return (')
        if return_pos < 0:
            raise RuntimeError('Retorno principal final do Dashboard não encontrado.')
        learning_gate = '''
  if (clinicLearningMode) {
    return (
      <ClinicLearningDashboard
        onOpenBilling={() => {
          setSection('billing');
          setClinicLearningMode(false);
        }}
      />
    );
  }
'''
        source = source[:return_pos] + learning_gate + source[return_pos:]

    path.write_text(source, encoding='utf-8')
    print('Clínica: área de aprendizagem conectada ao Dashboard final com injeção resiliente.')


def fix_clinic_learning_ui() -> None:
    jsx_path = Path('/frontend/src/ClinicLearningDashboard.jsx')
    css_path = Path('/frontend/src/clinic-learning-dashboard.css')
    if not jsx_path.exists() or not css_path.exists():
        return

    source = jsx_path.read_text(encoding='utf-8')

    old_profile_effect = '''  useEffect(() => {
    if (section === 'perfil' && !profileLoaded) loadProfile();
  }, [section, profileLoaded]);'''
    new_profile_effect = '''  useEffect(() => {
    if (!profileLoaded) loadProfile();
  }, [profileLoaded]);'''
    if old_profile_effect in source:
        source = source.replace(old_profile_effect, new_profile_effect, 1)

    scroll_lock = '''
  useEffect(() => {
    if (!mobileOpen) return undefined;
    const previousBodyOverflow = document.body.style.overflow;
    const previousHtmlOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previousBodyOverflow;
      document.documentElement.style.overflow = previousHtmlOverflow;
    };
  }, [mobileOpen]);
'''
    if 'previousBodyOverflow' not in source:
        anchor = new_profile_effect
        if anchor in source:
            source = source.replace(anchor, anchor + scroll_lock, 1)
        else:
            raise RuntimeError('Efeito de carregamento do perfil não localizado na Clínica.')

    jsx_path.write_text(source, encoding='utf-8')

    css = css_path.read_text(encoding='utf-8')
    marker = '/* clinic-mobile-fixes-v1 */'
    if marker not in css:
        css += '''
/* clinic-mobile-fixes-v1 */
.clinic-course-brand{justify-content:flex-start;position:relative;padding-left:0}
.clinic-course-brand img{width:96px;max-width:96px;height:96px;max-height:96px;object-fit:cover;object-position:center;mix-blend-mode:screen;clip-path:circle(42% at 50% 50%);margin-left:-14px;filter:saturate(1.08) contrast(1.04)}
.clinic-course-sidebar{overscroll-behavior:contain;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch}
.clinic-sidebar-backdrop{touch-action:none;overscroll-behavior:none}
.clinic-course-shell{overflow-x:hidden}
@media(max-width:820px){.clinic-course-sidebar{height:100dvh;max-height:100dvh;overscroll-behavior:contain}.clinic-course-brand{flex:0 0 auto;justify-content:flex-start;padding-left:0}.clinic-course-navigation{flex:0 0 auto}.clinic-course-account{flex:0 0 auto}.clinic-course-brand img{width:96px;max-width:96px;height:96px;max-height:96px;margin-left:-14px}.clinic-sidebar-close{position:absolute;right:4px;top:24px}}
'''
    css_path.write_text(css, encoding='utf-8')
    print('Clínica: logo alinhado à esquerda e recortado sem fundo quadrado; foto persistente e rolagem móvel isolada.')


def stabilize_runtime_patch() -> None:
    path = Path('/tmp/finalize_new_core_only.py')
    if not path.exists():
        return

    source = path.read_text(encoding='utf-8')
    unsafe = '''    artifact_result_anchor = '            "artifacts": artifacts,\\n'
    if 'artifacts = artifacts[:1]' not in source:
        position = source.find(artifact_result_anchor)
        if position < 0:
            raise RuntimeError('Resultado de artefatos não localizado no worker final.')
        source = source[:position] + '        artifacts = artifacts[:1]\\n' + source[position:]

'''
    if unsafe in source:
        source = source.replace(unsafe, '', 1)

    if "artifacts = artifacts[:1]" in source:
        raise RuntimeError('Inserção insegura de limite de artefatos permaneceu no patch final.')

    path.write_text(source, encoding='utf-8')
    compile(source, str(path), 'exec')
    print('Patch final estabilizado: limite de um arquivo preservado pela persistência canônica.')


stabilize_frontend()
connect_clinic_learning_dashboard()
fix_clinic_learning_ui()
stabilize_runtime_patch()

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
        raise RuntimeError('Payload JSON de /api/chat/respond não localizado no Dashboard final.')

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

    import_anchor = "import DOMNAI_LOGO from './assets/domnai-logo-oficial-transparente.png';"
    learning_import = "import ClinicLearningDashboard from './ClinicLearningDashboard';"
    if learning_import not in source:
        if import_anchor not in source:
            raise RuntimeError('Import principal do Dashboard não encontrada.')
        source = source.replace(import_anchor, import_anchor + '\n' + learning_import, 1)

    function_anchor = "export default function Dashboard() {\n  const { getToken } = useAuth();"
    function_replacement = "export default function Dashboard() {\n  const { getToken } = useAuth();\n  const [clinicLearningMode, setClinicLearningMode] = useState(true);"
    if 'const [clinicLearningMode, setClinicLearningMode]' not in source:
        if function_anchor not in source:
            raise RuntimeError('Início do Dashboard não encontrado.')
        source = source.replace(function_anchor, function_replacement, 1)

    open_anchor = "  function openDashboard() {\n    setSection('chat');"
    open_replacement = "  function openDashboard() {\n    setClinicLearningMode(true);\n    setSection('chat');"
    if open_replacement not in source:
        if open_anchor not in source:
            raise RuntimeError('Função openDashboard não encontrada.')
        source = source.replace(open_anchor, open_replacement, 1)

    return_anchor = "  return (\n    <main className=\"domnai-app-shell\">"
    learning_gate = """  if (clinicLearningMode) {
    return (
      <ClinicLearningDashboard
        onOpenBilling={() => {
          setSection('billing');
          setClinicLearningMode(false);
        }}
      />
    );
  }

  return (
    <main className=\"domnai-app-shell\">"""
    if '<ClinicLearningDashboard' not in source:
        if return_anchor not in source:
            raise RuntimeError('Retorno principal do Dashboard não encontrado.')
        source = source.replace(return_anchor, learning_gate, 1)

    path.write_text(source, encoding='utf-8')
    print('Clínica: modo aluno ativado; chat, biblioteca, lixeira e operações preservados no legado, porém fora da navegação principal.')


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
stabilize_runtime_patch()

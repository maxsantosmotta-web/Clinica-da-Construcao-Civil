from pathlib import Path

path = Path('/frontend/src/Dashboard.jsx')
source = path.read_text(encoding='utf-8')

import_anchor = "import DOMNAI_LOGO from './assets/domnai-logo-oficial-transparente.png';"
learning_import = "import ClinicLearningDashboard from './ClinicLearningDashboard';"
if learning_import not in source:
    if import_anchor not in source:
        raise RuntimeError('Import principal do Dashboard não encontrada.')
    source = source.replace(import_anchor, import_anchor + '\n' + learning_import, 1)

function_anchor = "export default function Dashboard() {\n  const { getToken } = useAuth();"
function_replacement = "export default function Dashboard() {\n  const { getToken } = useAuth();\n  const [clinicLearningMode, setClinicLearningMode] = useState(true);"
if 'clinicLearningMode' not in source:
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

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


def fix_clinic_admin_branding() -> None:
    admin_jsx = Path('/frontend/src/AdminAccessBoundary.jsx')
    admin_css = Path('/frontend/src/admin-access-boundary.css')
    app_jsx = Path('/frontend/src/App.jsx')

    if admin_jsx.exists():
        source = admin_jsx.read_text(encoding='utf-8')
        old_import = "import DOMNAI_LOGO from './assets/domnai-logo-oficial-transparente.png';"
        clinic_import = "import CLINIC_LOGO from './assets/clinic-logo-data.js';"
        if old_import in source:
            source = source.replace(old_import, clinic_import, 1)
        elif clinic_import not in source:
            first_import_end = source.find('\n')
            source = source[:first_import_end + 1] + clinic_import + '\n' + source[first_import_end + 1:]
        source = source.replace('src={DOMNAI_LOGO}', 'src={CLINIC_LOGO}')
        source = source.replace('alt="DomnAI"', 'alt="Clínica da Construção Civil"')
        source = source.replace('DomnAI · Administração', 'Clínica da Construção Civil · Administração')
        source = source.replace("email || 'Conta DomnAI'", "email || 'Clínica da Construção Civil'")
        admin_jsx.write_text(source, encoding='utf-8')

    if app_jsx.exists():
        source = app_jsx.read_text(encoding='utf-8')
        clinic_import = "import CLINIC_LOGO from './assets/clinic-logo-data.js';"
        if clinic_import not in source:
            domnai_import = "import DOMNAI_LOGO from './assets/domnai-logo-oficial-transparente.png';"
            if domnai_import in source:
                source = source.replace(domnai_import, domnai_import + '\n' + clinic_import, 1)
        landing_start = source.find('function Landing()')
        landing_end = source.find('\nfunction Home()', landing_start)
        if landing_start >= 0 and landing_end > landing_start:
            landing = source[landing_start:landing_end]
            landing = landing.replace('src={DOMNAI_LOGO}', 'src={CLINIC_LOGO}', 1)
            landing = landing.replace('DomnAI — Transforme escolhas em resultados com inteligência.', 'Clínica da Construção Civil', 1)
            source = source[:landing_start] + landing + source[landing_end:]
        app_jsx.write_text(source, encoding='utf-8')

    if admin_css.exists():
        css = admin_css.read_text(encoding='utf-8')
        marker = '/* clinic-admin-theme-v1 */'
        if marker not in css:
            css += '''
/* clinic-admin-theme-v1 */
.domnai-admin-gate-page,.domnai-admin-shell{background:#001b17!important;color:#f4fffc}
.domnai-admin-sidebar{background:linear-gradient(180deg,#00251f 0%,#001914 100%)!important;border-right-color:rgba(47,225,183,.18)!important}
.domnai-admin-workspace{background:#001b17!important}
.domnai-admin-brand{border-bottom-color:rgba(47,225,183,.16)!important;text-align:left}
.domnai-admin-brand img{width:92px!important;height:92px!important;max-width:92px!important;max-height:92px!important;object-fit:cover!important;object-position:center!important;clip-path:circle(43% at 50% 50%);mix-blend-mode:screen;filter:saturate(1.08) contrast(1.05)}
.domnai-admin-brand>span,.domnai-admin-topbar span:first-child,.domnai-admin-foundation-kicker{color:#35d9b3!important}
.domnai-admin-sidebar nav button.active{border-color:rgba(47,225,183,.42)!important;background:linear-gradient(90deg,rgba(47,225,183,.15),rgba(47,225,183,.05))!important;color:#75f1d5!important}
.domnai-admin-sidebar nav button.active span{color:#35d9b3!important}
.domnai-admin-open-menu,.domnai-admin-close-menu,.domnai-admin-back-user{border-color:rgba(47,225,183,.32)!important;background:#05251f!important;color:#64e6c7!important}
.domnai-admin-open-menu:hover,.domnai-admin-close-menu:hover,.domnai-admin-back-user:hover{background:rgba(47,225,183,.12)!important;border-color:rgba(47,225,183,.58)!important}
.domnai-admin-gate-card{border-color:rgba(47,225,183,.28)!important;background:linear-gradient(180deg,rgba(3,38,31,.98),rgba(1,23,19,.98))!important}
.domnai-admin-gate-card>img{width:116px!important;height:116px!important;max-height:116px!important;object-fit:cover!important;clip-path:circle(43% at 50% 50%);mix-blend-mode:screen}
.domnai-admin-spinner{border-color:rgba(47,225,183,.18)!important;border-top-color:#35d9b3!important}
.domnai-overview-hero{background:linear-gradient(135deg,rgba(8,52,43,.96),rgba(4,29,25,.98))!important;border-color:rgba(47,225,183,.18)!important}
.domnai-overview-metrics article{background:linear-gradient(180deg,#071c18,#04130f)!important;border-color:rgba(47,225,183,.12)!important}
.domnai-premium-chart-card{background:#050706!important;border-color:rgba(47,225,183,.12)!important}
.domnai-premium-chart-card::before{background:transparent!important}
.domnai-admin-premium-heading button{border-color:rgba(47,225,183,.28)!important;background:#05251f!important;color:#76efd5!important}
@media(max-width:820px){.domnai-admin-brand img{width:84px!important;height:84px!important;max-width:84px!important;max-height:84px!important}}
'''
        admin_css.write_text(css, encoding='utf-8')

    print('Clínica: ADM com identidade verde/turquesa, logo da Clínica, gráficos em fundo preto e transições sem logo DomnAI.')


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
fix_clinic_admin_branding()
stabilize_runtime_patch()

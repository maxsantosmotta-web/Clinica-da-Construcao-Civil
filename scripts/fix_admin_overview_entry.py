from pathlib import Path
import re

TARGET = Path('/frontend/src/AdminAccessBoundary.jsx')

source = TARGET.read_text(encoding='utf-8')

css_marker = "import './admin-premium-monitor.css';\n"
css_import = "import './admin-overview-entry-fixes.css';\n"
if css_import not in source:
    if source.count(css_marker) != 1:
        raise SystemExit('Importação premium não encontrada exatamente uma vez.')
    source = source.replace(css_marker, css_marker + css_import, 1)

state_pattern = re.compile(
    r"const \[activeSection, setActiveSection\] = useState\(\(\) => \{\s*"
    r"const saved = sessionStorage\.getItem\('domnai:admin-section:v1'\);\s*"
    r"return .*?;\s*\}\);",
    re.S,
)
source, state_count = state_pattern.subn(
    "const [activeSection, setActiveSection] = useState('Visão geral');",
    source,
    count=1,
)
if state_count != 1 and "const [activeSection, setActiveSection] = useState('Visão geral');" not in source:
    raise SystemExit(f'Estado persistente do módulo: esperado trecho antigo ou final, encontrado {state_count}.')

source = source.replace(
    "    sessionStorage.setItem('domnai:admin-section:v1', section);\n",
    '',
    1,
)

# O botão de retorno ao Painel Usuário já é montado pelos patches anteriores do build.
# Este script cuida somente da entrada da Visão geral e das métricas shadow.
TARGET.write_text(source, encoding='utf-8')

overview_target = Path('/frontend/src/AdminOverviewView.jsx')
overview = overview_target.read_text(encoding='utf-8')

replacements = [
    (
        ("  cutover: {},\n};",),
        "  cutover: {},\n  shadow: {},\n};",
        'estado shadow',
    ),
    (
        ("        ['cutover', '/api/admin/cutover?limit=1000', authorizedHeaders],\n        ['health', '/health', {}],",),
        "        ['cutover', '/api/admin/cutover?limit=1000', authorizedHeaders],\n        ['shadow', '/api/admin/shadow-validation?limit=1000', authorizedHeaders],\n        ['health', '/health', {}],",
        'requisição shadow',
    ),
    (
        ("  const cutoverSummary = data.cutover?.summary || {};",),
        "  const cutoverSummary = data.cutover?.summary || {};\n  const shadowSummary = data.shadow?.summary || {};",
        'resumo shadow',
    ),
    (
        (
            "          <article data-tone={data.cutover?.shadowApproved ? 'green' : 'gold'}><span>Validação shadow</span><strong>{data.cutover?.shadowApproved ? 'Aprovada' : 'Pendente'}</strong><small>{data.cutover?.requireShadowApproval ? 'aprovação obrigatória' : 'aprovação não exigida'}</small></article>",
            "          <article data-tone={shadowSummary.approved ? 'green' : 'gold'}><span>Validação shadow</span><strong>{shadowSummary.approved ? 'Aprovada' : 'Pendente'}</strong><small>{formatPercent(shadowSummary.success_rate)} de sucesso</small></article>",
            "          <article data-tone={shadowSummary.approved ? 'green' : 'gold'}><span>Validação comportamental</span><strong>{shadowSummary.approved ? 'Aprovada' : 'Pendente'}</strong><small>{formatPercent(shadowSummary.behavior_adherence_rate)} de aderência · meta 100%</small></article>",
        ),
        "          <article data-tone={shadowSummary.approved ? 'green' : 'gold'}><span>Validação comportamental</span><strong>{shadowSummary.approved ? 'Aprovada' : 'Pendente'}</strong><small>{formatPercent(shadowSummary.behavior_adherence_rate)} de aderência · meta 100%{shadowSummary.top_behavior_failure ? ` · falha: ${shadowSummary.top_behavior_failure}` : ''}</small></article>",
        'status comportamental',
    ),
    (
        (
            "          <article data-tone=\"purple\"><span>Amostras</span><strong>{formatNumber(cutoverSummary.sampleCount)}</strong><small>{formatNumber(cutoverSummary.newCoreResponses)} respostas do novo núcleo</small></article>",
            "          <article data-tone=\"purple\"><span>Amostras shadow</span><strong>{formatNumber(shadowSummary.sample_count)}</strong><small>{formatPercent(shadowSummary.non_empty_rate)} respostas não vazias · {formatPercent(shadowSummary.average_similarity)} similaridade</small></article>",
        ),
        "          <article data-tone=\"purple\"><span>Amostras comportamentais</span><strong>{formatNumber(shadowSummary.sample_count)}</strong><small>{formatPercent(shadowSummary.non_empty_rate)} não vazias · {formatPercent(shadowSummary.average_behavior_score)} qualidade média</small></article>",
        'amostras comportamentais',
    ),
]

for old_options, new, label in replacements:
    if new in overview:
        continue
    matched = next((old for old in old_options if old in overview), None)
    if matched is None:
        raise SystemExit(f'{label}: trecho esperado não encontrado.')
    overview = overview.replace(matched, new, 1)

# Leitura operacional final: OpenAI é auxiliar neste produto e não derruba a saúde principal.
# Erros estabilizados continuam no histórico, mas não contam como módulos atualmente afetados.
overview = overview.replace(
    "      Boolean(healthDependencies.openaiConfigured),\n",
    "      true, // OpenAI é opcional para a operação principal da Clínica.\n",
    1,
)
overview = overview.replace(
    "  const cutoverSummary = data.cutover?.summary || {};\n  const shadowSummary = data.shadow?.summary || {};",
    "  const cutoverSummary = data.cutover?.summary || {};\n  const shadowSummary = data.shadow?.summary || {};\n  const activeAffectedModules = new Set((data.errors?.items || []).filter((item) => item.status === 'active').map((item) => String(item.module || '').trim()).filter(Boolean)).size;",
    1,
)
overview = overview.replace(
    "<small>{formatNumber(errorsSummary.affectedModules)} módulos afetados</small>",
    "<small>{formatNumber(activeAffectedModules)} módulos afetados agora</small>",
    1,
)
overview = overview.replace(
    "<h1>{data.health?.statusLabel || (status === 'ready' ? 'Monitoramento ativo' : 'Sincronizando')}</h1>",
    "<h1>{status === 'ready' && healthDistribution[1].value === 0 ? 'Operacional' : data.health?.statusLabel || (status === 'ready' ? 'Monitoramento ativo' : 'Sincronizando')}</h1>",
    1,
)
overview = overview.replace(
    "<article data-tone=\"green\"><span>Saúde geral</span><strong>{data.health?.statusLabel || 'Verificando'}</strong><small>{formatNumber(data.health?.serverCheckMs)} ms internos</small></article>",
    "<article data-tone=\"green\"><span>Saúde geral</span><strong>{status === 'ready' && healthDistribution[1].value === 0 ? 'Operacional' : data.health?.statusLabel || 'Verificando'}</strong><small>{formatNumber(data.health?.serverCheckMs)} ms internos</small></article>",
    1,
)
overview_target.write_text(overview, encoding='utf-8')

# Saúde: OpenAI permanece visível como integração auxiliar, sem gerar atenção operacional.
health_target = Path('/frontend/src/AdminHealthView.jsx')
health = health_target.read_text(encoding='utf-8')
health = health.replace(
    "        status: serviceStatus(Boolean(dependencies.openaiConfigured)),\n        detail: dependencies.openaiConfigured ? 'Chave disponível no servidor' : 'Chave não configurada',",
    "        status: dependencies.openaiConfigured ? { state: 'ready', label: 'Configurado' } : { state: 'ready', label: 'Opcional' },\n        detail: dependencies.openaiConfigured ? 'Chave disponível no servidor' : 'Integração auxiliar; não exigida para a operação principal',",
    1,
)
health = health.replace(
    "      <section className={`domnai-admin-health-overall ${health.status === 'ok' && status === 'ready' ? 'ready' : 'attention'}`}>",
    "      <section className={`domnai-admin-health-overall ${status === 'ready' && attentionCount === 0 ? 'ready' : 'attention'}`}>",
    1,
)
health = health.replace(
    "          <strong>{status === 'ready' ? health.statusLabel : status === 'error' ? 'Indisponível' : 'Verificando...'}</strong>",
    "          <strong>{status === 'ready' && attentionCount === 0 ? 'Operacional' : status === 'ready' ? health.statusLabel : status === 'error' ? 'Indisponível' : 'Verificando...'}</strong>",
    1,
)
health = health.replace(
    "        API e banco são testados em cada atualização. OpenAI, Clerk e Stripe indicam se a configuração necessária está presente no servidor.",
    "        API e banco são testados em cada atualização. Clerk, Stripe e PDF compõem a operação principal. OpenAI é uma integração auxiliar e não reduz a saúde geral quando não configurada.",
    1,
)
health_target.write_text(health, encoding='utf-8')

# Erros: somente grupos ativos entram em “módulos afetados”; estabilizados ficam como histórico.
errors_target = Path('/frontend/src/AdminErrorsView.jsx')
errors = errors_target.read_text(encoding='utf-8')
errors = errors.replace(
    ".filter((item) => item.status !== 'resolved')",
    ".filter((item) => item.status === 'active')",
    1,
)
errors = errors.replace(
    "      setItems(Array.isArray(payload.items) ? payload.items : []);\n      setSummary({ ...EMPTY_SUMMARY, ...(payload.summary || {}) });",
    "      const nextItems = Array.isArray(payload.items) ? payload.items : [];\n      const activeModules = new Set(nextItems.filter((item) => item.status === 'active').map((item) => String(item.module || '').trim()).filter(Boolean)).size;\n      setItems(nextItems);\n      setSummary({ ...EMPTY_SUMMARY, ...(payload.summary || {}), affectedModules: activeModules });",
    1,
)
errors_target.write_text(errors, encoding='utf-8')

print('Painel ADM ajustado: saúde principal real, OpenAI opcional e módulos afetados somente por erros ativos.')

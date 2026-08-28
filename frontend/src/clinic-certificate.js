import CLINIC_LOGO from './assets/clinic-logo-data.js';
import './clinic-certificate.css';

const CERTIFICATE_STORAGE_KEY = 'clinic:certificate-completed-at';
let certificateModal = null;
let scheduled = false;

function readProgress() {
  const rings = [...document.querySelectorAll('.clinic-progress-ring span')];
  for (const ring of rings) {
    const value = Number.parseInt(String(ring.textContent || '').replace(/\D/g, ''), 10);
    if (Number.isFinite(value)) return value;
  }
  const progressTitle = [...document.querySelectorAll('.clinic-progress-card h2')]
    .map((node) => String(node.textContent || ''))
    .find((text) => /\d+\s+de\s+39\s+aulas/i.test(text));
  if (progressTitle) {
    const match = progressTitle.match(/(\d+)\s+de\s+39/i);
    if (match) return Math.round((Number(match[1]) / 39) * 100);
  }
  return 0;
}

function getCompletionDate(progress) {
  if (progress !== 100) return null;
  let stored = localStorage.getItem(CERTIFICATE_STORAGE_KEY);
  if (!stored) {
    stored = new Date().toISOString();
    localStorage.setItem(CERTIFICATE_STORAGE_KEY, stored);
  }
  const date = new Date(stored);
  return Number.isNaN(date.getTime()) ? new Date() : date;
}

function formatDate(date) {
  return date.toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo' });
}

function formatTime(date) {
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' });
}

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function certificateMarkup({ name, completionDate, typedSignature }) {
  const safeName = escapeHtml(name.trim());
  const studentSignature = typedSignature
    ? `<div class="student-signature typed">${safeName}</div>`
    : '<div class="student-signature manual"></div>';

  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Certificado de Conclusão</title>
<style>
  @page{size:A4 landscape;margin:0}
  *{box-sizing:border-box}
  body{margin:0;background:#e9e7df;font-family:Arial,Helvetica,sans-serif;color:#15212b}
  .sheet{width:297mm;height:210mm;margin:0 auto;background:#fffdf8;padding:12mm;position:relative;overflow:hidden}
  .frame{height:100%;border:3px solid #b38b2e;outline:1px solid #1d2d3b;outline-offset:-8px;padding:12mm 16mm;position:relative}
  .header{display:flex;align-items:center;gap:12mm}
  .logo{width:32mm;height:32mm;object-fit:contain}
  .brand{font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#1c3341}
  .title{text-align:center;margin-top:-13mm}
  .title h1{margin:0;font-size:30px;letter-spacing:.16em;color:#b38b2e}
  .title h2{margin:3px 0 0;font-size:16px;letter-spacing:.22em;color:#1d2d3b}
  .lead{text-align:center;margin:16mm 0 4mm;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
  .recipient{text-align:center;font-family:Georgia,serif;font-size:28px;font-weight:700;min-height:12mm;border-bottom:1px solid #b38b2e;max-width:190mm;margin:0 auto 8mm;padding-bottom:3mm}
  .statement{text-align:center;font-size:15px;line-height:1.55;max-width:220mm;margin:0 auto 8mm}
  .modules{border:1px solid #d7c48d;background:#fffaf0;padding:5mm 7mm;max-width:225mm;margin:0 auto 7mm}
  .modules-title{text-align:center;font-size:9px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3mm;color:#6e5720}
  .module-grid{display:grid;grid-template-columns:1fr 1fr;gap:10mm;font-size:9px;line-height:1.5}
  .module-grid strong{display:block;margin-bottom:1mm;font-size:10px;text-transform:uppercase;color:#1d2d3b}
  .disclaimer{text-align:center;font-size:8px;line-height:1.5;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#46535b;margin:0 auto 6mm}
  .footer{display:grid;grid-template-columns:1fr 1fr 1fr;align-items:end;gap:8mm;margin-top:4mm}
  .meta{font-size:9px;line-height:1.5;color:#34444d}
  .signature-wrap{text-align:center;font-size:8px;text-transform:uppercase;color:#5a6469}
  .student-signature{height:12mm;border-bottom:1px solid #293841;display:flex;align-items:flex-end;justify-content:center;padding-bottom:1mm;margin-bottom:2mm}
  .student-signature.typed{font-family:"Brush Script MT","Segoe Script",cursive;font-size:22px;text-transform:none;color:#172a34}
  .clinic-signature{height:12mm;border-bottom:1px solid #293841;display:flex;align-items:flex-end;justify-content:center;padding-bottom:1mm;margin-bottom:2mm;font-family:Georgia,serif;font-size:16px;font-weight:700;color:#1d2d3b;text-transform:none}
  .seal{position:absolute;left:50%;bottom:9mm;transform:translateX(-50%);width:24mm;height:24mm;border:2px solid #b38b2e;border-radius:50%;display:grid;place-items:center;color:#b38b2e;font-weight:800;font-size:8px;text-align:center;letter-spacing:.08em}
</style>
</head>
<body>
  <main class="sheet">
    <section class="frame">
      <div class="header"><img class="logo" src="${CLINIC_LOGO}" alt="Clínica da Construção Civil" /><div class="brand">Clínica da Construção Civil</div></div>
      <div class="title"><h1>CERTIFICADO</h1><h2>DE CONCLUSÃO</h2></div>
      <div class="lead">Certificamos para os devidos fins que</div>
      <div class="recipient">${safeName}</div>
      <div class="statement">Concluiu com êxito o treinamento completo com a carga horária de <strong>40h</strong>, do curso de elétrica e hidráulica.</div>
      <div class="modules">
        <div class="modules-title">Especificações do conteúdo que compôs o curso</div>
        <div class="module-grid">
          <div><strong>Elétrica</strong>Instalação de tomadas<br/>Chuveiros elétricos<br/>Interruptores e lâmpadas<br/>Quadros de Distribuição<br/>Normas NR10</div>
          <div><strong>Hidráulica</strong>Instalações residenciais<br/>Pressurização de rede<br/>Redes de água e esgoto<br/>Reparos e Vazamentos<br/>Reservatórios</div>
        </div>
      </div>
      <div class="disclaimer">Curso de formação livre, não profissionalizante.<br/>Não confere habilitação profissional.</div>
      <div class="footer">
        <div class="meta"><strong>Conclusão</strong><br/>Data: ${formatDate(completionDate)}<br/>Hora: ${formatTime(completionDate)}</div>
        <div class="signature-wrap">${studentSignature}<span>Assinatura do aluno</span></div>
        <div class="signature-wrap"><div class="clinic-signature">Clínica da Construção Civil</div><span>Responsável pelo curso</span></div>
      </div>
      <div class="seal">CCC<br/>40H</div>
    </section>
  </main>
  <script>window.addEventListener('load',()=>setTimeout(()=>window.print(),250));<\/script>
</body>
</html>`;
}

function closeCertificateModal() {
  certificateModal?.remove();
  certificateModal = null;
}

function openCertificateModal() {
  closeCertificateModal();
  const progress = readProgress();
  const completionDate = getCompletionDate(progress);
  const unlocked = progress === 100 && completionDate;

  certificateModal = document.createElement('div');
  certificateModal.className = 'clinic-certificate-overlay';
  certificateModal.innerHTML = `
    <section class="clinic-certificate-modal" role="dialog" aria-modal="true" aria-labelledby="clinic-certificate-title">
      <button type="button" class="clinic-certificate-close" aria-label="Fechar">×</button>
      <span class="clinic-certificate-kicker">Certificado de conclusão</span>
      <h2 id="clinic-certificate-title">${unlocked ? 'Seu certificado está disponível' : 'Certificado ainda bloqueado'}</h2>
      <p>${unlocked ? 'A conclusão foi reconhecida automaticamente pelo contador de progresso.' : `Seu progresso atual é ${progress}%. O certificado será liberado automaticamente quando o contador chegar a 100%.`}</p>
      ${unlocked ? `
        <div class="clinic-certificate-meta"><div><span>Data da conclusão</span><strong>${formatDate(completionDate)}</strong></div><div><span>Horário</span><strong>${formatTime(completionDate)}</strong></div></div>
        <label class="clinic-certificate-field"><span>Nome completo</span><input type="text" id="clinic-certificate-name" autocomplete="name" placeholder="Digite o nome que aparecerá no certificado" /></label>
        <fieldset class="clinic-certificate-signature-options"><legend>Assinatura do aluno</legend><label><input type="radio" name="clinic-certificate-signature" value="typed" checked /> Assinar digitando o nome</label><label><input type="radio" name="clinic-certificate-signature" value="manual" /> Deixar em branco para imprimir e assinar depois</label></fieldset>
        <div class="clinic-certificate-actions"><button type="button" class="clinic-certificate-generate">Visualizar / Imprimir certificado</button></div>
        <div class="clinic-certificate-message" aria-live="polite"></div>
      ` : `<div class="clinic-certificate-locked"><strong>${progress}%</strong><span>Progresso atual</span></div>`}
    </section>`;

  certificateModal.querySelector('.clinic-certificate-close').addEventListener('click', closeCertificateModal);
  certificateModal.addEventListener('click', (event) => { if (event.target === certificateModal) closeCertificateModal(); });

  if (unlocked) {
    const nameInput = certificateModal.querySelector('#clinic-certificate-name');
    const message = certificateModal.querySelector('.clinic-certificate-message');
    certificateModal.querySelector('.clinic-certificate-generate').addEventListener('click', () => {
      const name = nameInput.value.trim();
      if (name.length < 3) {
        message.textContent = 'Digite o nome completo antes de gerar o certificado.';
        nameInput.focus();
        return;
      }
      const signatureMode = certificateModal.querySelector('input[name="clinic-certificate-signature"]:checked')?.value || 'typed';
      const printWindow = window.open('', '_blank', 'noopener,noreferrer');
      if (!printWindow) {
        message.textContent = 'Não foi possível abrir a visualização. Libere pop-ups para este site e tente novamente.';
        return;
      }
      printWindow.document.open();
      printWindow.document.write(certificateMarkup({ name, completionDate, typedSignature: signatureMode === 'typed' }));
      printWindow.document.close();
    });
  }

  document.body.appendChild(certificateModal);
}

function ensureCertificateEntry() {
  const nav = document.querySelector('.clinic-course-navigation');
  if (!nav) return;
  let button = nav.querySelector('.clinic-certificate-nav-button');
  if (!button) {
    button = document.createElement('button');
    button.type = 'button';
    button.className = 'clinic-certificate-nav-button';
    button.innerHTML = '<span>▣</span> Certificado';
    button.addEventListener('click', openCertificateModal);
    const progressButton = [...nav.querySelectorAll('button')].find((item) => String(item.textContent || '').includes('Meu Progresso'));
    if (progressButton) progressButton.insertAdjacentElement('afterend', button);
    else nav.appendChild(button);
  }

  const progress = readProgress();
  if (progress === 100) {
    getCompletionDate(progress);
    button.classList.add('is-unlocked');
    button.title = 'Certificado disponível';
  } else {
    button.classList.remove('is-unlocked');
    button.title = `Certificado disponível ao concluir 100% do curso (${progress}% atual)`;
  }
}

function scheduleSync() {
  if (scheduled) return;
  scheduled = true;
  window.setTimeout(() => {
    scheduled = false;
    ensureCertificateEntry();
  }, 60);
}

const observer = new MutationObserver(scheduleSync);
observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
window.addEventListener('hashchange', scheduleSync);
window.addEventListener('load', scheduleSync);
scheduleSync();

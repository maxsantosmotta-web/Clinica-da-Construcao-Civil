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

function safeFileName(name) {
  return String(name || 'aluno')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'aluno';
}

async function getClerkToken() {
  try {
    if (window.Clerk?.session?.getToken) return await window.Clerk.session.getToken();
  } catch {}
  return null;
}

async function generateCertificatePdf({ name, completionDate, typedSignature }) {
  const token = await getClerkToken();
  if (!token) throw new Error('Não foi possível confirmar sua sessão. Atualize a página e tente novamente.');

  const response = await fetch('/api/certificate/pdf', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      name,
      completed_at: completionDate.toISOString(),
      typed_signature: typedSignature,
      logo_data_uri: CLINIC_LOGO,
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Não foi possível gerar o certificado em PDF.');
  }

  const blob = await response.blob();
  if (!blob.size) throw new Error('O arquivo do certificado foi gerado vazio. Tente novamente.');
  const filename = `Certificado-${safeFileName(name)}.pdf`;
  return { blob, filename };
}

function downloadPdf(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 30000);
}

async function sharePdf(blob, filename) {
  const file = new File([blob], filename, { type: 'application/pdf' });
  if (navigator.share && navigator.canShare?.({ files: [file] })) {
    await navigator.share({
      title: 'Certificado de Conclusão',
      text: 'Certificado de Conclusão — Clínica da Construção Civil',
      files: [file],
    });
    return true;
  }
  return false;
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
      <h2 id="clinic-certificate-title">${unlocked ? 'Seu certificado está disponível' : 'Certificado bloqueado'}</h2>
      <p>${unlocked ? 'A conclusão foi reconhecida automaticamente pelo contador de progresso.' : `Seu progresso atual é ${progress}%. O certificado será liberado automaticamente quando o contador chegar a 100%.`}</p>
      ${unlocked ? `
        <div class="clinic-certificate-meta"><div><span>Data da conclusão</span><strong>${formatDate(completionDate)}</strong></div><div><span>Horário</span><strong>${formatTime(completionDate)}</strong></div></div>
        <label class="clinic-certificate-field"><span>Nome completo</span><input type="text" id="clinic-certificate-name" autocomplete="name" placeholder="Digite o nome que aparecerá no certificado" /></label>
        <fieldset class="clinic-certificate-signature-options"><legend>Assinatura do aluno</legend><label><input type="radio" name="clinic-certificate-signature" value="typed" checked /> Assinar digitando o nome</label><label><input type="radio" name="clinic-certificate-signature" value="manual" /> Deixar em branco para imprimir e assinar depois</label></fieldset>
        <div class="clinic-certificate-actions">
          <button type="button" class="clinic-certificate-generate">Baixar certificado em PDF</button>
          <button type="button" class="clinic-certificate-share">Compartilhar certificado</button>
        </div>
        <div class="clinic-certificate-message" aria-live="polite"></div>
      ` : `<div class="clinic-certificate-locked"><strong>${progress}%</strong><span>Progresso atual</span></div>`}
    </section>`;

  certificateModal.querySelector('.clinic-certificate-close').addEventListener('click', closeCertificateModal);
  certificateModal.addEventListener('click', (event) => { if (event.target === certificateModal) closeCertificateModal(); });

  if (unlocked) {
    const nameInput = certificateModal.querySelector('#clinic-certificate-name');
    const message = certificateModal.querySelector('.clinic-certificate-message');
    const downloadButton = certificateModal.querySelector('.clinic-certificate-generate');
    const shareButton = certificateModal.querySelector('.clinic-certificate-share');

    async function createPdf() {
      const name = nameInput.value.trim();
      if (name.length < 3) {
        message.textContent = 'Digite o nome completo antes de gerar o certificado.';
        nameInput.focus();
        return null;
      }
      const signatureMode = certificateModal.querySelector('input[name="clinic-certificate-signature"]:checked')?.value || 'typed';
      return generateCertificatePdf({ name, completionDate, typedSignature: signatureMode === 'typed' });
    }

    downloadButton.addEventListener('click', async () => {
      message.textContent = 'Gerando seu certificado em PDF...';
      downloadButton.disabled = true;
      shareButton.disabled = true;
      try {
        const result = await createPdf();
        if (!result) return;
        downloadPdf(result.blob, result.filename);
        message.textContent = `Certificado gerado: ${result.filename}`;
      } catch (error) {
        message.textContent = error.message || 'Não foi possível gerar o certificado.';
      } finally {
        downloadButton.disabled = false;
        shareButton.disabled = false;
      }
    });

    shareButton.addEventListener('click', async () => {
      message.textContent = 'Preparando o arquivo do certificado...';
      downloadButton.disabled = true;
      shareButton.disabled = true;
      try {
        const result = await createPdf();
        if (!result) return;
        const shared = await sharePdf(result.blob, result.filename);
        if (!shared) {
          downloadPdf(result.blob, result.filename);
          message.textContent = 'O compartilhamento direto não é suportado neste aparelho. O PDF foi baixado para você compartilhar pelo gerenciador de arquivos.';
        } else {
          message.textContent = 'Certificado preparado para compartilhamento.';
        }
      } catch (error) {
        if (error?.name === 'AbortError') {
          message.textContent = '';
        } else {
          message.textContent = error.message || 'Não foi possível compartilhar o certificado.';
        }
      } finally {
        downloadButton.disabled = false;
        shareButton.disabled = false;
      }
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

import './clinic-certificate.css';

function certificateStorageKey() {
  const userId = window.__clinicCourseProgress?.userId || 'local';
  return `clinic:certificate-completed-at:${userId}`;
}

let certificateModal = null;
let scheduled = false;

function readProgress() {
  const liveProgress = Number(window.__clinicCourseProgress?.progress);
  if (Number.isFinite(liveProgress)) return liveProgress;
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
  const storageKey = certificateStorageKey();
  if (progress !== 100) {
    localStorage.removeItem(storageKey);
    return null;
  }
  let stored = localStorage.getItem(storageKey);
  if (!stored) {
    stored = new Date().toISOString();
    localStorage.setItem(storageKey, stored);
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

async function getClerkToken() {
  try {
    if (window.Clerk?.session?.getToken) return await window.Clerk.session.getToken();
  } catch {}
  return null;
}

async function certificateFetch(path, options = {}) {
  const token = await getClerkToken();
  if (!token) throw new Error('Não foi possível confirmar sua sessão. Atualize a página e tente novamente.');
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
    cache: 'no-store',
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Não foi possível acessar o certificado.');
  }
  return response;
}

async function getCertificateStatus() {
  const response = await certificateFetch('/api/certificate/status');
  return response.json();
}

async function issueCertificate({ name, completionDate, typedSignature }) {
  const response = await certificateFetch('/api/certificate/issue', {
    method: 'POST',
    body: JSON.stringify({ name, completed_at: completionDate.toISOString(), typed_signature: typedSignature }),
  });
  const blob = await response.blob();
  if (!blob.size) throw new Error('O arquivo do certificado foi gerado vazio. Tente novamente.');
  return blob;
}

async function getCurrentCertificate() {
  const response = await certificateFetch('/api/certificate/pdf');
  const blob = await response.blob();
  if (!blob.size) throw new Error('O arquivo do certificado está vazio. Tente novamente.');
  return blob;
}

function openPdf(blob) {
  const url = URL.createObjectURL(blob);
  const opened = window.open(url, '_blank', 'noopener,noreferrer');
  if (!opened) {
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
  window.setTimeout(() => URL.revokeObjectURL(url), 60000);
}

async function sharePdf(blob, filename) {
  const file = new File([blob], filename || 'Certificado.pdf', { type: 'application/pdf' });
  if (navigator.share && navigator.canShare?.({ files: [file] })) {
    await navigator.share({ title: 'Certificado de Conclusão', text: 'Certificado de Conclusão — Clínica da Construção Civil', files: [file] });
    return true;
  }
  return false;
}

function closeCertificateModal() {
  certificateModal?.remove();
  certificateModal = null;
}

function escaped(value) {
  return String(value || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function signatureOptions(typedSignature = true) {
  return `<fieldset class="clinic-certificate-signature-options"><legend>Assinatura do aluno</legend><label><input type="radio" name="clinic-certificate-signature" value="typed" ${typedSignature ? 'checked' : ''} /> Assinar digitando o nome</label><label><input type="radio" name="clinic-certificate-signature" value="manual" ${typedSignature ? '' : 'checked'} /> Deixar em branco para imprimir e assinar depois</label></fieldset>`;
}

function issuanceForm({ completionDate, currentName = '', typedSignature = true, correction = false }) {
  return `<div class="clinic-certificate-meta"><div><span>Data da conclusão</span><strong>${formatDate(completionDate)}</strong></div><div><span>Horário</span><strong>${formatTime(completionDate)}</strong></div></div><label class="clinic-certificate-field"><span>Nome completo</span><input type="text" id="clinic-certificate-name" autocomplete="name" value="${escaped(currentName)}" placeholder="Digite o nome que aparecerá no certificado" /></label>${signatureOptions(typedSignature)}<div class="clinic-certificate-actions"><button type="button" class="clinic-certificate-issue">${correction ? 'Emitir correção do certificado' : 'Emitir certificado'}</button></div><div class="clinic-certificate-message" aria-live="polite"></div>`;
}

async function openCertificateModal() {
  closeCertificateModal();
  const progress = readProgress();
  const completionDate = getCompletionDate(progress);
  const unlocked = progress === 100 && completionDate;

  certificateModal = document.createElement('div');
  certificateModal.className = 'clinic-certificate-overlay';
  certificateModal.innerHTML = `<section class="clinic-certificate-modal" role="dialog" aria-modal="true" aria-labelledby="clinic-certificate-title"><button type="button" class="clinic-certificate-close" aria-label="Fechar">×</button><span class="clinic-certificate-kicker">Certificado de conclusão</span><h2 id="clinic-certificate-title">${unlocked ? 'Seu certificado está disponível' : 'Certificado bloqueado'}</h2><div class="clinic-certificate-body">${unlocked ? '<p>Carregando seu certificado...</p>' : `<p>Seu progresso atual é ${progress}%. O certificado será liberado automaticamente quando o contador chegar a 100%.</p><div class="clinic-certificate-locked"><strong>${progress}%</strong><span>Progresso atual</span></div>`}</div></section>`;

  certificateModal.querySelector('.clinic-certificate-close').addEventListener('click', closeCertificateModal);
  certificateModal.addEventListener('click', (event) => { if (event.target === certificateModal) closeCertificateModal(); });
  document.body.appendChild(certificateModal);
  if (!unlocked) return;

  const body = certificateModal.querySelector('.clinic-certificate-body');

  async function showIssuedState(status, messageText = '') {
    body.innerHTML = `<p>${status.locked ? 'Certificado definitivo emitido. Os dados estão bloqueados.' : 'Certificado emitido. Você ainda possui uma correção disponível.'}</p><div class="clinic-certificate-meta"><div><span>Nome emitido</span><strong>${escaped(status.name)}</strong></div><div><span>Emissões utilizadas</span><strong>${status.issue_count}/2</strong></div></div><div class="clinic-certificate-actions"><button type="button" class="clinic-certificate-open">Abrir certificado</button><button type="button" class="clinic-certificate-share">Compartilhar certificado</button>${status.locked ? '' : '<button type="button" class="clinic-certificate-correct">Corrigir nome/assinatura</button>'}</div><div class="clinic-certificate-message" aria-live="polite">${escaped(messageText)}</div>`;
    const message = body.querySelector('.clinic-certificate-message');
    const setBusy = (busy) => [...body.querySelectorAll('button')].forEach((button) => { button.disabled = busy; });

    body.querySelector('.clinic-certificate-open').addEventListener('click', async () => {
      setBusy(true); message.textContent = 'Abrindo seu certificado...';
      try { openPdf(await getCurrentCertificate()); message.textContent = ''; }
      catch (error) { message.textContent = error.message || 'Não foi possível abrir o certificado.'; }
      finally { setBusy(false); }
    });

    body.querySelector('.clinic-certificate-share').addEventListener('click', async () => {
      setBusy(true); message.textContent = 'Preparando o certificado para compartilhar...';
      try {
        const blob = await getCurrentCertificate();
        const shared = await sharePdf(blob, status.filename);
        if (!shared) { openPdf(blob); message.textContent = 'O compartilhamento direto não é suportado neste aparelho. O certificado foi aberto para você usar a opção de compartilhar do visualizador.'; }
        else message.textContent = '';
      } catch (error) {
        if (error?.name === 'AbortError') message.textContent = '';
        else message.textContent = error.message || 'Não foi possível compartilhar o certificado.';
      } finally { setBusy(false); }
    });

    body.querySelector('.clinic-certificate-correct')?.addEventListener('click', () => {
      body.innerHTML = issuanceForm({ completionDate, currentName: status.name || '', typedSignature: status.typed_signature !== false, correction: true });
      bindIssueForm(true);
    });
  }

  function bindIssueForm(correction = false) {
    const nameInput = body.querySelector('#clinic-certificate-name');
    const message = body.querySelector('.clinic-certificate-message');
    const issueButton = body.querySelector('.clinic-certificate-issue');
    issueButton.addEventListener('click', async () => {
      const name = nameInput.value.trim();
      if (name.length < 3) { message.textContent = 'Digite o nome completo antes de emitir o certificado.'; nameInput.focus(); return; }
      const signatureMode = body.querySelector('input[name="clinic-certificate-signature"]:checked')?.value || 'typed';
      issueButton.disabled = true;
      message.textContent = correction ? 'Emitindo a correção...' : 'Emitindo seu certificado...';
      try {
        const blob = await issueCertificate({ name, completionDate, typedSignature: signatureMode === 'typed' });
        openPdf(blob);
        const status = await getCertificateStatus();
        await showIssuedState(status, correction ? 'Correção emitida. Este certificado agora é definitivo.' : 'Certificado emitido com sucesso.');
      } catch (error) { message.textContent = error.message || 'Não foi possível emitir o certificado.'; }
      finally { issueButton.disabled = false; }
    });
  }

  try {
    const status = await getCertificateStatus();
    if (status.issued) await showIssuedState(status);
    else { body.innerHTML = `<p>A conclusão foi reconhecida pelo contador de progresso. Confira os dados antes da primeira emissão.</p>${issuanceForm({ completionDate })}`; bindIssueForm(false); }
  } catch (error) {
    body.innerHTML = `<p class="clinic-certificate-message">${escaped(error.message || 'Não foi possível carregar o certificado.')}</p>`;
  }
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
    if (progressButton) progressButton.insertAdjacentElement('afterend', button); else nav.appendChild(button);
  }
  const progress = readProgress();
  if (progress === 100) { getCompletionDate(progress); button.classList.add('is-unlocked'); button.title = 'Certificado disponível'; }
  else { getCompletionDate(progress); button.classList.remove('is-unlocked'); button.title = `Certificado disponível ao concluir 100% do curso (${progress}% atual)`; }
}

function scheduleSync() {
  if (scheduled) return;
  scheduled = true;
  window.setTimeout(() => { scheduled = false; ensureCertificateEntry(); }, 60);
}

const observer = new MutationObserver(scheduleSync);
observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
window.addEventListener('hashchange', scheduleSync);
window.addEventListener('clinic-course-progress', scheduleSync);
window.addEventListener('load', scheduleSync);
scheduleSync();

function isHttpUrl(value) {
  return /^https?:\/\//i.test(String(value || '').trim());
}

function copyLink(value, button) {
  const text = String(value || '').trim();
  if (!text) return;

  const done = () => {
    const original = button.textContent;
    button.textContent = 'Copiado';
    window.setTimeout(() => {
      button.textContent = original;
    }, 1400);
  };

  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(() => {});
    return;
  }

  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  textarea.remove();
  done();
}

function enhanceLinkCard(card) {
  if (!(card instanceof HTMLElement) || card.dataset.linkEnhanced === 'true') return;

  const strong = card.querySelector('.native-file-copy strong');
  const url = strong?.textContent?.trim();
  if (!isHttpUrl(url)) return;

  card.dataset.linkEnhanced = 'true';
  card.classList.add('is-real-link');

  const badge = card.querySelector('.native-file-badge');
  const size = card.querySelector('.native-file-copy small');
  const action = card.querySelector('.native-file-action');

  if (badge) badge.textContent = 'LINK';
  if (size) size.remove();
  if (action) action.textContent = 'Abrir link';

  card.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    window.open(url, '_blank', 'noopener,noreferrer');
  }, true);

  const wrapper = card.closest('.chat-native-file, .composer-native-file');
  if (!wrapper || wrapper.querySelector('.copy-link-button')) return;

  const copyButton = document.createElement('button');
  copyButton.type = 'button';
  copyButton.className = 'copy-link-button';
  copyButton.textContent = 'Copiar link';
  copyButton.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    copyLink(url, copyButton);
  });

  const deleteButton = wrapper.querySelector('.native-delete-button, :scope > button:last-child');
  if (deleteButton) wrapper.insertBefore(copyButton, deleteButton);
  else wrapper.appendChild(copyButton);
}

const institutionalPages = {
  '/sobre': {
    kicker: 'Clínica da Construção Civil',
    title: 'Sobre a Clínica da Construção Civil',
    intro: 'A Clínica da Construção Civil é um treinamento prático para quem deseja aprender serviços essenciais da construção civil de forma simples, acessível e aplicável no dia a dia.',
    sections: [
      ['Nossa proposta', 'Ensinar na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil, com conteúdo organizado para facilitar o aprendizado mesmo para quem está começando.'],
      ['Como funciona', 'O aluno aprende por meio de aulas em vídeo, apostilas e materiais complementares, podendo estudar no próprio ritmo e consultar o conteúdo sempre que precisar.'],
      ['Para quem é', 'Para quem quer resolver problemas do dia a dia, desenvolver novas habilidades ou transformar conhecimento em oportunidade de prestação de serviços e geração de renda.'],
      ['Nosso compromisso', 'Entregar conteúdo objetivo, prático e responsável, incentivando sempre o uso correto de ferramentas, equipamentos de proteção e boas práticas de segurança.'],
    ],
  },
  '/privacidade': {
    kicker: 'Clínica da Construção Civil',
    title: 'Política de Privacidade',
    intro: 'A sua privacidade é importante para nós. Esta política explica de forma clara como os dados necessários ao funcionamento da plataforma podem ser tratados.',
    sections: [
      ['Dados de cadastro', 'Podemos tratar dados como nome, e-mail e identificadores de conta quando necessários para cadastro, autenticação, acesso ao treinamento, suporte e segurança da plataforma.'],
      ['Dados de uso', 'Informações técnicas e registros de utilização podem ser processados para manter o serviço funcionando, prevenir abusos, corrigir falhas e melhorar a experiência do usuário.'],
      ['Pagamentos', 'Quando houver contratação de plano ou assinatura, os pagamentos poderão ser processados por provedores especializados. A Clínica da Construção Civil não precisa armazenar os dados completos do cartão utilizado na transação.'],
      ['Compartilhamento', 'Os dados não são vendidos. O compartilhamento ocorre somente quando necessário para operação do serviço, cumprimento de obrigações legais ou proteção da plataforma e de seus usuários.'],
      ['Segurança e direitos', 'Adotamos medidas razoáveis de proteção. O usuário pode solicitar informações, correção ou exclusão de dados, observadas as obrigações legais e os registros necessários para segurança e cumprimento de contratos.'],
    ],
  },
  '/termos': {
    kicker: 'Clínica da Construção Civil',
    title: 'Termos de Uso',
    intro: 'Ao acessar ou utilizar a Clínica da Construção Civil, o usuário declara estar de acordo com estes termos e com as regras aplicáveis ao uso da plataforma e de seus conteúdos.',
    sections: [
      ['Uso da plataforma', 'O acesso é destinado ao estudo e aprendizado pessoal do conteúdo disponibilizado. O usuário deve utilizar a plataforma de forma lícita, responsável e sem tentar comprometer seu funcionamento ou a conta de terceiros.'],
      ['Conteúdo educacional', 'As aulas e materiais têm finalidade educacional. Atividades de elétrica, hidráulica, manutenção e construção envolvem riscos e devem respeitar normas técnicas, equipamentos de proteção, limites de qualificação e, quando necessário, acompanhamento de profissional habilitado.'],
      ['Conta e acesso', 'O usuário é responsável por manter seus dados de acesso protegidos e por informar dados verdadeiros no cadastro. O compartilhamento indevido de conta pode resultar em restrição ou suspensão de acesso.'],
      ['Propriedade intelectual', 'Textos, aulas, apostilas, materiais, identidade visual e demais conteúdos da plataforma são protegidos e não podem ser reproduzidos, revendidos ou distribuídos sem autorização.'],
      ['Planos e alterações', 'Preços, planos, funcionalidades e conteúdos podem ser atualizados ao longo do tempo, respeitando as condições aplicáveis às contratações já realizadas e a legislação vigente.'],
    ],
  },
  '/ajuda': {
    kicker: 'Central de ajuda',
    title: 'Como podemos ajudar?',
    intro: 'Encontre orientações rápidas para começar a utilizar a Clínica da Construção Civil.',
    help: [
      ['Como criar sua conta', 'Na tela inicial, toque em “Criar conta”, informe seu e-mail e senha ou utilize o acesso com Google. Depois, conclua a verificação solicitada.'],
      ['Como fazer login', 'Toque em “Fazer login” e utilize o mesmo método escolhido no cadastro.'],
      ['Esqueci minha senha', 'Na tela de login, escolha a recuperação de senha, informe seu e-mail, confirme o código recebido e crie uma nova senha.'],
      ['Como acessar o conteúdo', 'Após entrar na sua conta e possuir acesso válido ao treinamento, os módulos, aulas e materiais disponíveis aparecem dentro da plataforma.'],
      ['Problemas de acesso', 'Confira primeiro sua conexão, o e-mail utilizado no cadastro e se a verificação de acesso foi concluída. Se o problema persistir, utilize o canal de suporte disponibilizado na plataforma.'],
    ],
    faq: [
      ['Preciso ter experiência em construção civil?', 'Não. O conteúdo foi organizado para facilitar o aprendizado inclusive de quem está começando.'],
      ['Posso estudar pelo celular?', 'Sim. A plataforma foi preparada para funcionar em celulares, tablets e computadores.'],
      ['Posso estudar no meu ritmo?', 'Sim. Você pode avançar de acordo com sua disponibilidade e revisar os materiais sempre que o seu acesso estiver ativo.'],
      ['As aulas substituem um profissional habilitado?', 'Não. O treinamento é educacional e não substitui exigências legais, normas técnicas, responsabilidade técnica ou atuação de profissional habilitado quando isso for obrigatório.'],
    ],
  },
};

function currentInstitutionalRoute() {
  const hash = window.location.hash.replace(/^#/, '').split('?')[0].replace(/\/$/, '') || '/';
  return institutionalPages[hash] ? hash : null;
}

function applyInstitutionalBranding() {
  const route = currentInstitutionalRoute();
  if (!route) return;

  const page = institutionalPages[route];
  const contentCard = document.querySelector('.content-card');
  if (!contentCard) return;

  const header = document.querySelector('.content-header');
  const brandLink = header?.querySelector('.brand-link');
  const brandImg = brandLink?.querySelector('img');
  if (brandImg) {
    brandImg.style.display = 'none';
    brandImg.setAttribute('alt', 'Clínica da Construção Civil');
  }
  if (brandLink && !brandLink.querySelector('.clinic-institutional-brand')) {
    const brand = document.createElement('span');
    brand.className = 'clinic-institutional-brand';
    brand.textContent = 'CLÍNICA DA CONSTRUÇÃO CIVIL';
    brand.style.color = '#f5f7f7';
    brand.style.fontWeight = '800';
    brand.style.fontSize = 'clamp(.86rem, 3vw, 1.08rem)';
    brand.style.letterSpacing = '.08em';
    brandLink.appendChild(brand);
  }
  if (brandLink) brandLink.setAttribute('aria-label', 'Voltar para a Clínica da Construção Civil');

  const kicker = contentCard.querySelector('.content-kicker');
  const title = contentCard.querySelector('h1');
  const intro = contentCard.querySelector('.content-intro');
  if (kicker) kicker.textContent = page.kicker;
  if (title) title.textContent = page.title;
  if (intro) intro.textContent = page.intro;

  if (route !== '/ajuda') {
    const sectionsContainer = contentCard.querySelector('.content-sections');
    if (sectionsContainer && sectionsContainer.dataset.clinicContent !== route) {
      sectionsContainer.dataset.clinicContent = route;
      sectionsContainer.innerHTML = page.sections.map(([sectionTitle, text]) => (
        `<section><h2>${sectionTitle}</h2><p>${text}</p></section>`
      )).join('');
    }
    return;
  }

  const helpGrid = contentCard.querySelector('.help-grid');
  if (helpGrid && helpGrid.dataset.clinicContent !== 'help') {
    helpGrid.dataset.clinicContent = 'help';
    helpGrid.innerHTML = page.help.map(([sectionTitle, text]) => (
      `<section class="help-item"><h2>${sectionTitle}</h2><p>${text}</p></section>`
    )).join('');
  }

  const faqList = contentCard.querySelector('.faq-list');
  if (faqList && faqList.dataset.clinicContent !== 'faq') {
    faqList.dataset.clinicContent = 'faq';
    faqList.innerHTML = page.faq.map(([question, answer]) => (
      `<details><summary>${question}</summary><p>${answer}</p></details>`
    )).join('');
  }
}

function enhanceDashboard() {
  document.querySelectorAll('.message-author').forEach((element) => element.remove());
  document.querySelectorAll('.native-file-card.link, .native-file-card.file').forEach(enhanceLinkCard);
  applyInstitutionalBranding();
}

const observer = new MutationObserver(enhanceDashboard);

function start() {
  enhanceDashboard();
  observer.observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener('hashchange', () => window.setTimeout(enhanceDashboard, 0));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start, { once: true });
} else {
  start();
}

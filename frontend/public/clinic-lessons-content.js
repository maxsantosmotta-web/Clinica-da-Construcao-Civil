(() => {
  const titles = [
    'Grandezas elétricas e conceito atômico',
    'Diferença de corrente contínua e alternada',
    'Cálculos básicos da elétrica (triângulo da tensão e da potência)',
    'Condutores elétricos: tipos (barramento, cabo e fio) e padrão de cores dos cabos',
    'Emendas elétricas (fio a fio) e isolantes elétricos',
    'Emendas com conectores elétricos',
    'Dimensionamento de cabos (conforme NBR 5410)',
    'Segurança em serviços elétricos e EPIs (NR-10)',
    'Disjuntores (tipos, aplicação, função, funcionamento e dimensionamento)',
    'DPS (tipos, aplicação, função, funcionamento e dimensionamento)',
    'IDR (tipos, aplicação, função, funcionamento e dimensionamento)',
    'Ferramentas básicas de um eletricista e a função de cada uma',
    'Como usar multímetro e alicate amperímetro',
    'Instalação de interruptor simples',
    'Instalação de interruptor duplo e triplo',
    'Instalação de interruptor paralelo (three way) e intermediário (four way)',
    'Instalação de tomadas conforme NBR 14136 e divisão de circuito conforme NBR 5410',
    'Instalação de tomadas simples, dupla e tripla, de 10 e 20 amperes na prática',
    'Instalação de tomada com interruptor no mesmo ponto',
    'Instalação de sensor de presença (com e sem interruptor)',
    'Instalação hidráulica: principais componentes de uma residência',
    'Instalações de água fria: fundamentos e evolução das redes prediais — NBR 5626',
    'Assista a este vídeo primeiro e depois faça a drenagem do seu banheiro',
    "Aprenda como instalar válvula na caixa d'água para aumentar pressão de chuveiro e torneiras",
    'Como aumentar a pressão da água',
    'Como fazer caixa de esgoto de concreto',
    'Instalação de bomba pressurizadora',
    'Como fazer a instalação de água fria e esgoto de banheiro, cozinha e área de serviço',
    'Tratamento de esgoto',
    'Faça sua casa — esgoto da casa 17',
    'Veja como é fácil achar vazamento de água',
    'Como identificar vazamento na parede',
    "Caixa d'água: instalação fácil em poucos passos!",
    'Como desentupir pia em minutos com ajuda da furadeira',
    'Como desentupir vaso em 1 minuto',
    'Como desentupir ralo de banheiro sem precisar quebrar',
    "Como limpar a caixa d'água: 10 passos para higienização da caixa d'água",
    "Como consertar caixa d'água vazando pelo ladrão — água/vazamento 001",
    "Caixa d'água: veja como instalar — Dicas do Fernando"
  ];

  const styleId = 'clinic-course-content-style';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .clinic-welcome-block{margin:24px 0 8px;padding:24px;border:1px solid rgba(79,225,194,.22);border-radius:20px;background:linear-gradient(145deg,#0b201b,#081713);box-shadow:0 18px 48px rgba(0,0,0,.16)}
      .clinic-welcome-block>span{display:block;color:#58e4c7;font-size:.74rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px}
      .clinic-welcome-block h2{margin:0 0 10px;font-size:clamp(1.35rem,2.2vw,1.9rem);line-height:1.25;color:#f7fffd}
      .clinic-welcome-block p{margin:0;max-width:850px;color:#9db4ad;line-height:1.65}
      .clinic-module-transition{grid-column:1/-1;margin:12px 0 4px;padding:24px;border:1px solid rgba(79,225,194,.28);border-radius:20px;background:linear-gradient(135deg,rgba(24,134,111,.22),rgba(8,25,21,.96));text-align:center}
      .clinic-module-transition strong{display:block;color:#5be7ca;font-size:clamp(1.15rem,2.4vw,1.65rem);letter-spacing:.045em;text-transform:uppercase}
      .clinic-module-transition span{display:block;margin-top:8px;color:#a6bbb5;line-height:1.55}
      .clinic-lesson-cover>img.clinic-approved-cover{position:absolute!important;inset:0!important;top:0!important;left:0!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;object-fit:cover!important;object-position:center!important;mix-blend-mode:normal!important;filter:none!important}
      @media(max-width:820px){.clinic-welcome-block{padding:20px 18px}.clinic-module-transition{padding:20px 16px}.clinic-lesson-actions{flex-wrap:wrap}}
    `;
    document.head.appendChild(style);
  }

  function ensureWelcome() {
    const filter = document.querySelector('.clinic-filter-row');
    if (!filter || document.querySelector('.clinic-welcome-block')) return;
    const welcome = document.createElement('section');
    welcome.className = 'clinic-welcome-block';
    welcome.innerHTML = '<span>BEM-VINDO À CLÍNICA DA CONSTRUÇÃO CIVIL</span><h2>Bem-vindo ao treinamento! Agora é hora de transformar conhecimento em prática e novas oportunidades.</h2><p>Estude no seu ritmo, com aulas práticas e conteúdo direto ao ponto para você aplicar o que aprender no dia a dia.</p>';
    filter.parentNode.insertBefore(welcome, filter);
  }

  function lessonIndexForCard(card, position, activeFilter) {
    if (activeFilter === 'hidráulica') return 20 + position;
    if (activeFilter === 'elétrica') return position;
    return position;
  }

  function applyLessonContent() {
    const grid = document.querySelector('.clinic-lessons-grid');
    if (!grid) return;
    ensureWelcome();

    const activeFilter = (document.querySelector('.clinic-filter-row button.is-active')?.textContent || 'Todos').trim().toLowerCase();
    const cards = [...grid.querySelectorAll('.clinic-lesson-card')];

    cards.forEach((card, position) => {
      const index = lessonIndexForCard(card, position, activeFilter);
      const title = titles[index];
      if (!title) return;

      const heading = card.querySelector('.clinic-lesson-copy h2');
      if (heading) {
        const value = `${index + 1}. ${title}`;
        if (heading.textContent !== value) heading.textContent = value;
      }

      const description = card.querySelector('.clinic-lesson-copy p');
      const moduleName = index < 20 ? 'Elétrica' : 'Hidráulica';
      if (description) {
        const value = `Aula prática do módulo de ${moduleName}.`;
        if (description.textContent !== value) description.textContent = value;
      }

      const cover = card.querySelector('.clinic-lesson-cover img');
      if (cover) {
        if (!cover.src.endsWith('/clinic-lesson-cover.webp')) cover.src = '/clinic-lesson-cover.webp';
        cover.classList.add('clinic-approved-cover');
        cover.alt = `Capa da aula ${index + 1} — ${title}`;
      }
    });

    const oldTransition = grid.querySelector('.clinic-module-transition');
    if (activeFilter === 'todos' && cards.length >= 21) {
      if (!oldTransition) {
        const transition = document.createElement('section');
        transition.className = 'clinic-module-transition';
        transition.innerHTML = '<strong>VOCÊ CONCLUIU O MÓDULO DE ELÉTRICA!</strong><span>AGORA É HORA DE AVANÇAR PARA O MÓDULO DE HIDRÁULICA.<br>Continue no seu ritmo e coloque em prática tudo o que aprender nas próximas aulas.</span>';
        cards[19].insertAdjacentElement('afterend', transition);
      }
    } else if (oldTransition) {
      oldTransition.remove();
    }
  }

  let scheduled = false;
  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      applyLessonContent();
    });
  };

  const observer = new MutationObserver(schedule);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('click', (event) => {
    if (event.target.closest('.clinic-filter-row button')) setTimeout(schedule, 0);
  }, true);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', schedule, { once: true });
  else schedule();
})();
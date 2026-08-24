# Clínica da Construção Civil

Plataforma de cursos da **Clínica da Construção Civil**.

**Subtítulo oficial:** Aprenda na prática elétrica, hidráulica, manutenção e serviços essenciais da construção civil.

## Proposta

A Clínica da Construção Civil é um treinamento prático desenvolvido para quem deseja aprender serviços essenciais da construção civil de forma simples e acessível. A plataforma reunirá aulas em vídeo, apostilas e materiais complementares sobre elétrica, hidráulica, manutenção e reparos, permitindo ao aluno estudar no próprio ritmo e acompanhar sua evolução até a conclusão do curso.

## Planos oficiais

- **Mensal:** R$ 10,90/mês
- **Anual promocional:** R$ 99,00/ano

## Estrutura técnica reaproveitada

Este repositório nasceu como uma cópia independente da base técnica do DomnAI e será adaptado exclusivamente para a Clínica da Construção Civil.

A base atualmente inclui:

- Backend Python com FastAPI e Uvicorn.
- Frontend React com Vite.
- Autenticação com Clerk.
- PostgreSQL com SQLAlchemy.
- Migrações versionadas com Alembic.
- Faturamento recorrente com Stripe.
- Estrutura administrativa e de usuários.
- Deploy preparado para Railway.

## Direção da adaptação

Serão preservados os componentes úteis de autenticação, usuários, banco, faturamento e infraestrutura. Serão removidos os recursos específicos do DomnAI que não fazem parte do produto educacional, como chat, biblioteca de arquivos do usuário, lixeira, créditos e motores de inteligência voltados à tomada de decisão.

A nova plataforma será organizada como área do aluno, com módulos de aulas, materiais complementares, acompanhamento de progresso, assinatura e certificado.

## Certificação automática

O certificado deverá ser emitido automaticamente quando o aluno atingir 100% de conclusão das aulas obrigatórias.

O fluxo previsto é:

1. cada aula obrigatória registra status de conclusão;
2. o sistema calcula o progresso do aluno;
3. ao atingir 100%, o backend valida a conclusão;
4. o sistema gera automaticamente o certificado;
5. o certificado é vinculado à conta do aluno e fica disponível para acesso.

Os dados necessários para emissão serão obtidos do cadastro do usuário, incluindo nome completo e demais informações definidas para certificação.

## Banco de dados e migrações

O projeto usa Alembic. Mudanças estruturais no banco devem ser feitas por migrações versionadas em `migrations/versions`.

## Estado atual

A cópia independente da base DomnAI foi concluída. O próximo estágio é mapear e adaptar os módulos da nova plataforma sem alterar o repositório original do DomnAI.

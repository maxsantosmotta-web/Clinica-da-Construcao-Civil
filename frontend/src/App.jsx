import React, { useState } from 'react';
import {
  AuthenticateWithRedirectCallback,
  useAuth,
  useSignIn,
  useSignUp,
} from '@clerk/clerk-react';
import { Link, Navigate, Route, Routes } from 'react-router-dom';
import Dashboard from './Dashboard';
import CourseVideoUpload from './CourseVideoUpload';
import DOMNAI_LOGO from './assets/domnai-logo-oficial-transparente.png';

function FooterNavigation() {
  return (
    <footer className="landing-footer" aria-label="Links institucionais">
      <Link to="/sobre">Sobre</Link>
      <Link to="/privacidade">Privacidade</Link>
      <Link to="/termos">Termos</Link>
      <Link to="/ajuda">Ajuda</Link>
    </footer>
  );
}

function getClerkError(error, fallback) {
  return error?.errors?.[0]?.longMessage || error?.errors?.[0]?.message || error?.message || fallback;
}

function GoogleIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20">
      <path fill="#4285F4" d="M21.6 12.23c0-.71-.06-1.24-.2-1.8H12v3.4h5.52a4.74 4.74 0 0 1-2.05 3.02v2.2h3.31c1.94-1.78 3.06-4.41 3.06-6.82Z" />
      <path fill="#34A853" d="M12 22c2.77 0 5.1-.91 6.78-2.48l-3.31-2.2c-.92.62-2.1.99-3.47.99-2.67 0-4.94-1.8-5.75-4.23H2.83v2.27A10.24 10.24 0 0 0 12 22Z" />
      <path fill="#FBBC05" d="M6.25 14.08A6.1 6.1 0 0 1 5.93 12c0-.72.12-1.42.32-2.08V7.65H2.83A10.02 10.02 0 0 0 1.75 12c0 1.57.38 3.05 1.08 4.35l3.42-2.27Z" />
      <path fill="#EA4335" d="M12 5.69c1.5 0 2.85.52 3.91 1.52l2.94-2.94C17.1 2.64 14.77 1.75 12 1.75a10.24 10.24 0 0 0-9.17 5.9l3.42 2.27C7.06 7.49 9.33 5.69 12 5.69Z" />
    </svg>
  );
}

function AuthModal({ mode, onClose, onSwitch }) {
  const { isLoaded: signInLoaded, signIn, setActive: setSignInActive } = useSignIn();
  const { isLoaded: signUpLoaded, signUp, setActive: setSignUpActive } = useSignUp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newPasswordConfirmation, setNewPasswordConfirmation] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState('form');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const isSignUp = mode === 'sign-up';
  const isReady = isSignUp ? signUpLoaded : signInLoaded;

  function returnToLogin() { setError(''); setCode(''); setNewPassword(''); setNewPasswordConfirmation(''); setStep('form'); }
  async function prepareEmailSecondFactor(attempt) {
    const emailFactor = attempt.supportedSecondFactors?.find((factor) => factor.strategy === 'email_code');
    if (!emailFactor) throw new Error('Não foi possível confirmar este acesso neste dispositivo.');
    await signIn.prepareSecondFactor({ strategy: 'email_code', emailAddressId: emailFactor.emailAddressId });
    setCode(''); setStep('second-factor');
  }
  async function handleGoogle() {
    setError('');
    if (!signInLoaded || !signIn) return setError('A autenticação ainda está carregando. Tente novamente.');
    setLoading(true);
    try { await signIn.authenticateWithRedirect({ strategy: 'oauth_google', redirectUrl: `${window.location.origin}/#/sso-callback`, redirectUrlComplete: `${window.location.origin}/#/` }); }
    catch (authError) { setError(getClerkError(authError, 'Não foi possível continuar com o Google.')); setLoading(false); }
  }
  async function handleCredentials(event) {
    event.preventDefault(); setError('');
    if (!isReady) return setError('A autenticação ainda está carregando. Tente novamente.');
    if (!email.trim() || !password) return setError('Informe o e-mail e a senha.');
    if (isSignUp && password !== confirmPassword) return setError('As senhas não coincidem.');
    setLoading(true);
    try {
      if (isSignUp) { await signUp.create({ emailAddress: email.trim(), password }); await signUp.prepareEmailAddressVerification({ strategy: 'email_code' }); setCode(''); setStep('verification'); }
      else {
        const attempt = await signIn.create({ identifier: email.trim(), password });
        if (attempt.status === 'complete') { await setSignInActive({ session: attempt.createdSessionId }); onClose(); return; }
        if (attempt.status === 'needs_second_factor') await prepareEmailSecondFactor(attempt); else throw new Error('O acesso exige uma etapa adicional não disponível.');
      }
    } catch (authError) { setError(getClerkError(authError, isSignUp ? 'Não foi possível criar a conta.' : 'E-mail ou senha inválidos.')); }
    finally { setLoading(false); }
  }
  async function handleCode(event) {
    event.preventDefault(); setError(''); if (!code.trim()) return setError('Digite o código recebido por e-mail.'); setLoading(true);
    try {
      if (step === 'verification') { const attempt = await signUp.attemptEmailAddressVerification({ code: code.trim() }); if (attempt.status !== 'complete') throw new Error('A verificação ainda não foi concluída.'); await setSignUpActive({ session: attempt.createdSessionId }); }
      else { const attempt = await signIn.attemptSecondFactor({ strategy: 'email_code', code: code.trim() }); if (attempt.status !== 'complete') throw new Error('A confirmação ainda não foi concluída.'); await setSignInActive({ session: attempt.createdSessionId }); }
      onClose();
    } catch (authError) { setError(getClerkError(authError, 'Código inválido ou expirado.')); } finally { setLoading(false); }
  }
  async function handlePasswordResetRequest(event) {
    event.preventDefault(); setError(''); if (!signInLoaded || !signIn) return setError('A autenticação ainda está carregando. Tente novamente.'); if (!email.trim()) return setError('Informe o e-mail da sua conta.'); setLoading(true);
    try { await signIn.create({ strategy: 'reset_password_email_code', identifier: email.trim() }); setCode(''); setStep('reset-code'); } catch (authError) { setError(getClerkError(authError, 'Não foi possível enviar o código de recuperação.')); } finally { setLoading(false); }
  }
  async function handlePasswordResetCode(event) {
    event.preventDefault(); setError(''); if (!code.trim()) return setError('Digite o código recebido por e-mail.'); setLoading(true);
    try { const attempt = await signIn.attemptFirstFactor({ strategy: 'reset_password_email_code', code: code.trim() }); if (attempt.status !== 'needs_new_password') throw new Error('A recuperação ainda não foi validada.'); setStep('reset-password'); } catch (authError) { setError(getClerkError(authError, 'Código inválido ou expirado.')); } finally { setLoading(false); }
  }
  async function handleNewPassword(event) {
    event.preventDefault(); setError(''); if (!newPassword || !newPasswordConfirmation) return setError('Informe e confirme a nova senha.'); if (newPassword !== newPasswordConfirmation) return setError('As senhas não coincidem.'); setLoading(true);
    try { const attempt = await signIn.resetPassword({ password: newPassword }); if (attempt.status === 'complete') { await setSignInActive({ session: attempt.createdSessionId }); onClose(); return; } if (attempt.status === 'needs_second_factor') { await prepareEmailSecondFactor(attempt); return; } throw new Error('Não foi possível concluir a redefinição da senha.'); } catch (authError) { setError(getClerkError(authError, 'Não foi possível criar a nova senha.')); } finally { setLoading(false); }
  }

  return <div className="custom-auth-backdrop" role="presentation" onMouseDown={onClose}><section className="custom-auth-card" role="dialog" aria-modal="true" aria-labelledby="auth-title" onMouseDown={(event) => event.stopPropagation()}><button className="custom-auth-close" type="button" onClick={onClose} aria-label="Fechar">×</button>
    {step === 'form' ? <><header className="custom-auth-header"><h1 id="auth-title">{isSignUp ? 'Criar sua conta' : 'Entrar no DomnAI'}</h1><p>{isSignUp ? 'Preencha seus dados para começar.' : 'Acesse sua conta para continuar.'}</p></header><button className="google-auth-button" type="button" onClick={handleGoogle} disabled={loading}><GoogleIcon /><span>Continuar com Google</span></button><div className="auth-divider"><span>ou</span></div><form className="custom-auth-form" onSubmit={handleCredentials}><label><span>E-mail</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Digite seu e-mail" autoComplete="email" inputMode="email" /></label><label><span>Senha</span><input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Digite sua senha" autoComplete={isSignUp ? 'new-password' : 'current-password'} /></label>{isSignUp ? <label><span>Confirmar senha</span><input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} placeholder="Digite a senha novamente" autoComplete="new-password" /></label> : <button className="custom-auth-back" type="button" onClick={() => { setError(''); setStep('reset-request'); }}>Esqueci minha senha</button>}<div id="clerk-captcha" />{error ? <p className="custom-auth-error" role="alert">{error}</p> : null}<button className="custom-auth-submit" type="submit" disabled={loading}>{loading ? 'Aguarde...' : isSignUp ? 'Criar conta' : 'Entrar'}</button></form><footer className="custom-auth-footer"><span>{isSignUp ? 'Já possui uma conta?' : 'Ainda não tem uma conta?'}</span><button type="button" onClick={() => onSwitch(isSignUp ? 'sign-in' : 'sign-up')}>{isSignUp ? 'Fazer login' : 'Criar conta'}</button></footer></> : null}
    {step === 'verification' || step === 'second-factor' ? <><header className="custom-auth-header"><h1 id="auth-title">Confirme seu e-mail</h1><p>Enviamos um código para <strong>{email}</strong>.</p></header><form className="custom-auth-form" onSubmit={handleCode}><label><span>Código de verificação</span><input type="text" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="Digite o código" inputMode="numeric" autoComplete="one-time-code" /></label>{error ? <p className="custom-auth-error" role="alert">{error}</p> : null}<button className="custom-auth-submit" type="submit" disabled={loading}>{loading ? 'Verificando...' : 'Confirmar acesso'}</button><button className="custom-auth-back" type="button" onClick={() => setStep('form')}>Voltar</button></form></> : null}
    {step === 'reset-request' ? <><header className="custom-auth-header"><h1 id="auth-title">Recuperar senha</h1><p>Informe o e-mail usado na sua conta.</p></header><form className="custom-auth-form" onSubmit={handlePasswordResetRequest}><label><span>E-mail</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Digite seu e-mail" autoComplete="email" inputMode="email" /></label>{error ? <p className="custom-auth-error" role="alert">{error}</p> : null}<button className="custom-auth-submit" type="submit" disabled={loading}>{loading ? 'Enviando...' : 'Enviar código'}</button><button className="custom-auth-back" type="button" onClick={returnToLogin}>Voltar ao login</button></form></> : null}
    {step === 'reset-code' ? <><header className="custom-auth-header"><h1 id="auth-title">Confirme o código</h1><p>Enviamos um código de recuperação para <strong>{email}</strong>.</p></header><form className="custom-auth-form" onSubmit={handlePasswordResetCode}><label><span>Código de recuperação</span><input type="text" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="Digite o código" inputMode="numeric" autoComplete="one-time-code" /></label>{error ? <p className="custom-auth-error" role="alert">{error}</p> : null}<button className="custom-auth-submit" type="submit" disabled={loading}>{loading ? 'Verificando...' : 'Confirmar código'}</button><button className="custom-auth-back" type="button" onClick={() => setStep('reset-request')}>Voltar</button></form></> : null}
    {step === 'reset-password' ? <><header className="custom-auth-header"><h1 id="auth-title">Criar nova senha</h1><p>Defina uma nova senha para acessar sua conta.</p></header><form className="custom-auth-form" onSubmit={handleNewPassword}><label><span>Nova senha</span><input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} placeholder="Digite a nova senha" autoComplete="new-password" /></label><label><span>Confirmar nova senha</span><input type="password" value={newPasswordConfirmation} onChange={(event) => setNewPasswordConfirmation(event.target.value)} placeholder="Digite a senha novamente" autoComplete="new-password" /></label>{error ? <p className="custom-auth-error" role="alert">{error}</p> : null}<button className="custom-auth-submit" type="submit" disabled={loading}>{loading ? 'Salvando...' : 'Salvar nova senha'}</button><button className="custom-auth-back" type="button" onClick={returnToLogin}>Cancelar</button></form></> : null}
  </section></div>;
}

function Landing() {
  const [authMode, setAuthMode] = useState(null);
  return <main className="landing-page"><section className="landing-card" aria-label="Acesso ao DomnAI"><img className="official-logo" src={DOMNAI_LOGO} alt="DomnAI — Transforme escolhas em resultados com inteligência." /><div className="access-actions"><button className="primary-button" type="button" onClick={() => setAuthMode('sign-up')}>Criar conta</button><button className="secondary-button" type="button" onClick={() => setAuthMode('sign-in')}>Fazer login</button></div></section><FooterNavigation />{authMode ? <AuthModal key={authMode} mode={authMode} onClose={() => setAuthMode(null)} onSwitch={setAuthMode} /> : null}</main>;
}
function Home() { const { isLoaded, isSignedIn } = useAuth(); return isLoaded && isSignedIn ? <Dashboard /> : <Landing />; }
function ProtectedVideoUpload() { const { isLoaded, isSignedIn } = useAuth(); if (!isLoaded) return null; return isSignedIn ? <CourseVideoUpload /> : <Navigate to="/" replace />; }
const institutionalContent = { sobre: { title: 'Sobre o DomnAI', intro: 'O DomnAI é uma plataforma de apoio à decisão criada para transformar escolhas em resultados com inteligência.', sections: [['Nossa proposta', 'Ajudar pessoas a pesquisar, analisar e comparar informações importantes antes de tomar uma decisão.'], ['Como ajudamos', 'Organizamos riscos, vantagens, alternativas e pontos de atenção para tornar cada escolha mais clara e segura.'], ['Nossa visão', 'Tornar análises inteligentes acessíveis para decisões do dia a dia, negócios, contratos, produtos e serviços.']] }, privacidade: { title: 'Privacidade', intro: 'Tratamos dados pessoais e informações enviadas à plataforma com responsabilidade, segurança e transparência.', sections: [['Dados de acesso', 'Podemos utilizar informações essenciais de cadastro e autenticação para permitir o uso seguro da plataforma.'], ['Conteúdo analisado', 'As informações fornecidas pelo usuário são utilizadas para gerar as análises solicitadas e melhorar a experiência do serviço.'], ['Segurança', 'Aplicamos práticas técnicas e operacionais para proteger dados contra acesso indevido, perda ou uso não autorizado.']] }, termos: { title: 'Termos de Uso', intro: 'Ao utilizar o DomnAI, o usuário concorda em usar a plataforma de forma responsável e de acordo com estes princípios.', sections: [['Uso da plataforma', 'O DomnAI oferece apoio informativo à tomada de decisão e não substitui orientação jurídica, contábil, médica ou financeira profissional.'], ['Responsabilidade do usuário', 'O usuário é responsável pelas informações fornecidas e pelas decisões tomadas a partir das análises apresentadas.'], ['Evolução do serviço', 'Recursos, planos e funcionalidades poderão evoluir conforme o desenvolvimento da plataforma.']] } };
function InstitutionalPage({ page }) { const content = institutionalContent[page]; return <main className="content-page"><header className="content-header"><Link className="brand-link" to="/"><img src={DOMNAI_LOGO} alt="DomnAI" /></Link><Link className="back-link" to="/">Voltar</Link></header><article className="content-card"><span className="content-kicker">DomnAI</span><h1>{content.title}</h1><p className="content-intro">{content.intro}</p><div className="content-sections">{content.sections.map(([title, text]) => <section key={title}><h2>{title}</h2><p>{text}</p></section>)}</div></article><FooterNavigation /></main>; }
function HelpPage() { return <main className="content-page"><header className="content-header"><Link className="brand-link" to="/"><img src={DOMNAI_LOGO} alt="DomnAI" /></Link><Link className="back-link" to="/">Voltar</Link></header><article className="content-card help-card"><span className="content-kicker">Central de ajuda</span><h1>Como podemos ajudar?</h1><p className="content-intro">Encontre orientações rápidas para começar a utilizar o DomnAI.</p></article><FooterNavigation /></main>; }
export default function App() { return <Routes><Route path="/" element={<Home />} /><Route path="/sso-callback" element={<AuthenticateWithRedirectCallback />} /><Route path="/video-aulas" element={<ProtectedVideoUpload />} /><Route path="/login/*" element={<Navigate to="/" replace />} /><Route path="/cadastro/*" element={<Navigate to="/" replace />} /><Route path="/sobre" element={<InstitutionalPage page="sobre" />} /><Route path="/privacidade" element={<InstitutionalPage page="privacidade" />} /><Route path="/termos" element={<InstitutionalPage page="termos" />} /><Route path="/ajuda" element={<HelpPage />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>; }

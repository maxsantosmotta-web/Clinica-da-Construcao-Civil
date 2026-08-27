from pathlib import Path

path = Path('/frontend/src/ClinicLearningDashboard.jsx')
text = path.read_text(encoding='utf-8')

old_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''
new_nav = '''          <button type="button" className={section === 'complementares' ? 'is-active' : ''} onClick={() => navigate('complementares')}><span>▤</span> Guias</button>
          <button type="button" className={section === 'complementares-drive' ? 'is-active' : ''} onClick={() => navigate('complementares-drive')}><span>▤</span> Complementares</button>
          <button type="button" className={section === 'ferramentas' ? 'is-active' : ''} onClick={() => navigate('ferramentas')}><span>✓</span> Ferramentas Práticas</button>'''

if "navigate('complementares-drive')" not in text:
    if old_nav not in text:
        raise RuntimeError('Navegação validada de Complementares/Ferramentas não encontrada; nada foi alterado.')
    text = text.replace(old_nav, new_nav, 1)

ferramentas_anchor = '''        {section === 'ferramentas' ? <>{selectedMaterial ? <section className="clinic-material-reader">'''
new_section = '''        {section === 'complementares-drive' ? <section className="clinic-material-reader"><div className="clinic-material-cover-frame"><div className="clinic-material-cover-pending"><span>Materiais complementares</span><strong>Clínica da Construção Civil</strong><small>Capa pronta para vinculação</small></div></div><button type="button" className="clinic-pdf-button" disabled>Acessar link</button></section> : null}\n\n'''

if "section === 'complementares-drive' ? <section" not in text:
    if ferramentas_anchor not in text:
        raise RuntimeError('Âncora da tela Ferramentas Práticas não encontrada; nada foi alterado.')
    text = text.replace(ferramentas_anchor, new_section + ferramentas_anchor, 1)

path.write_text(text, encoding='utf-8')
print('Menu atualizado: Guias preservado, novo Complementares criado e Ferramentas Práticas preservado.')

import React, { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Link } from 'react-router-dom';

export default function CourseVideoUpload() {
  const { getToken } = useAuth();
  const [lessonId, setLessonId] = useState(1);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [uploading, setUploading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setStatus('Selecione o arquivo MP4 da aula.');
      return;
    }

    setUploading(true);
    setStatus('Enviando vídeo...');
    try {
      const token = await getToken();
      const body = new FormData();
      body.append('file', file, file.name);
      const response = await fetch(`/api/videos/admin/aula-${lessonId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível enviar o vídeo.');
      setStatus(`Aula ${lessonId} enviada com sucesso.`);
      setFile(null);
      event.currentTarget.reset();
    } catch (error) {
      setStatus(error.message || 'Não foi possível enviar o vídeo.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <main style={{ minHeight: '100vh', background: '#0b0b0b', color: '#fff', padding: '32px 18px' }}>
      <section style={{ maxWidth: 620, margin: '0 auto', background: '#171717', border: '1px solid #333', borderRadius: 18, padding: 24 }}>
        <Link to="/" style={{ color: '#d4af37', textDecoration: 'none' }}>← Voltar</Link>
        <h1 style={{ marginBottom: 8 }}>Vídeos do curso</h1>
        <p style={{ color: '#bbb', marginTop: 0 }}>Envie o MP4 diretamente para a aula correspondente.</p>
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 16, marginTop: 24 }}>
          <label style={{ display: 'grid', gap: 8 }}>
            <span>Aula</span>
            <select value={lessonId} onChange={(event) => setLessonId(Number(event.target.value))} style={{ padding: 12, borderRadius: 10 }}>
              {Array.from({ length: 39 }, (_, index) => index + 1).map((id) => <option key={id} value={id}>Aula {id}</option>)}
            </select>
          </label>
          <label style={{ display: 'grid', gap: 8 }}>
            <span>Arquivo de vídeo</span>
            <input type="file" accept="video/mp4,video/*" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>
          <button type="submit" disabled={uploading} style={{ padding: 14, border: 0, borderRadius: 10, fontWeight: 700, cursor: 'pointer' }}>
            {uploading ? 'Enviando...' : 'Enviar vídeo'}
          </button>
        </form>
        {status ? <p role="status" style={{ marginTop: 18 }}>{status}</p> : null}
      </section>
    </main>
  );
}

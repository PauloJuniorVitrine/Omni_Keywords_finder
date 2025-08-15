import { test, expect, request } from '@playwright/test';

const API_BASE = 'http://127.0.0.1:5000/api';

test.describe('Governança - E2E API', () => {
  test('Processar keywords - sucesso', async ({ request }) => {
    const payload = {
      keywords: [
        { termo: 'kw_teste', volume_busca: 100, cpc: 1.5, concorrencia: 0.5, intencao: 'informacional' }
      ]
    };
    const resp = await request.post(`${API_BASE}/processar_keywords`, { data: payload });
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    expect(data.keywords[0].termo).toBe('kw_teste');
    expect(data.relatorio.status).toBe('ok');
  });

  test('Exportar keywords - JSON', async ({ request }) => {
    const resp = await request.get(`${API_BASE}/exportar_keywords?formato=json&prefix=kw_`);
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data[0].termo).toContain('kw_');
  });

  test('Exportar keywords - CSV', async ({ request }) => {
    const resp = await request.get(`${API_BASE}/exportar_keywords?formato=csv&prefix=kw_`);
    expect(resp.status()).toBe(200);
    const text = await resp.text();
    expect(text).toContain('termo,score');
  });

  test('Governança logs - sucesso', async ({ request }) => {
    const resp = await request.get(`${API_BASE}/governanca/logs?event=validacao_keywords`);
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    expect(Array.isArray(data.logs)).toBeTruthy();
  });

  test('Governança logs - erro de parâmetro', async ({ request }) => {
    const resp = await request.get(`${API_BASE}/governanca/logs?event=@@@@`);
    expect(resp.status()).toBe(400);
    const data = await resp.json();
    expect(data.erro).toContain('inválido');
  });

  test('Upload de regras - sucesso', async ({ request }) => {
    const payload = {
      score_minimo: 0.7,
      blacklist: ['kw_banida'],
      whitelist: ['kw_livre']
    };
    const resp = await request.post(`${API_BASE}/governanca/regras/upload`, { data: payload });
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    expect(data.status).toBe('ok');
  });

  test('Upload de regras - erro', async ({ request }) => {
    const payload = { score_minimo: null, blacklist: [], whitelist: [] };
    const resp = await request.post(`${API_BASE}/governanca/regras/upload`, { data: payload });
    expect(resp.status()).toBe(422);
    const data = await resp.json();
    expect(data.erro).toContain('score_minimo');
  });

  test('Editar regras - sucesso', async ({ request }) => {
    const payload = {
      score_minimo: 0.8,
      blacklist: ['kw_banida2'],
      whitelist: ['kw_livre2']
    };
    const resp = await request.post(`${API_BASE}/governanca/regras/editar`, { data: payload });
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    expect(data.status).toBe('ok');
  });

  test('Editar regras - erro', async ({ request }) => {
    const payload = { score_minimo: null, blacklist: [], whitelist: [] };
    const resp = await request.post(`${API_BASE}/governanca/regras/editar`, { data: payload });
    expect(resp.status()).toBe(422);
    const data = await resp.json();
    expect(data.erro).toContain('score_minimo');
  });

  test('Processar keywords - apenas cauda longa', async ({ request }) => {
    const payload = {
      keywords: [
        { termo: 'curta', volume_busca: 100, cpc: 1.5, concorrencia: 0.4, intencao: 'informacional' },
        { termo: 'duas palavras', volume_busca: 100, cpc: 1.5, concorrencia: 0.4, intencao: 'informacional' },
        { termo: 'palavra chave cauda longa exemplo', volume_busca: 100, cpc: 1.5, concorrencia: 0.4, intencao: 'informacional' },
        { termo: 'termo muito curto', volume_busca: 100, cpc: 1.5, concorrencia: 0.4, intencao: 'informacional' },
        { termo: 'palavra chave cauda longa relevante para teste', volume_busca: 100, cpc: 1.5, concorrencia: 0.4, intencao: 'informacional' },
        { termo: 'tres palavras', volume_busca: 100, cpc: 1.5, concorrencia: 0.6, intencao: 'informacional' }
      ]
    };
    const resp = await request.post(`${API_BASE}/processar_keywords`, { data: payload });
    expect(resp.status()).toBe(200);
    const data = await resp.json();
    const termos = data.keywords.map((k: any) => k.termo);
    expect(termos).toContain('palavra chave cauda longa exemplo');
    expect(termos).toContain('palavra chave cauda longa relevante para teste');
    expect(termos).not.toContain('curta');
    expect(termos).not.toContain('duas palavras');
    expect(termos).not.toContain('termo muito curto');
    expect(termos).not.toContain('tres palavras');
    for (const k of data.keywords) {
      expect(k.termo.split(' ').length).toBeGreaterThanOrEqual(3);
      expect(k.termo.length).toBeGreaterThanOrEqual(15);
      expect(k.concorrencia).toBeLessThanOrEqual(0.5);
    }
  });
}); 
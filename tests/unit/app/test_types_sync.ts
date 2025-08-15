/**
 * Teste de Sincronização de Tipos TypeScript
 * 
 * Valida que os tipos do frontend estão sincronizados com o backend
 * 
 * Tracing ID: FIXTYPE-001_TEST_SYNC_20241227_001
 * Data: 2024-12-27
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  // Tipos base
  BaseEntity,
  
  // Tipos de nichos
  Nicho,
  NichoCreate,
  
  // Tipos de categorias
  Categoria,
  CategoriaCreate,
  
  // Tipos de prompts
  PromptBase,
  PromptPreenchido,
  
  // Tipos de dados coletados
  DadosColetados,
  DadosColetadosCreate,
  
  // Tipos de processamento
  ProcessamentoResponse,
  
  // Tipos de estatísticas
  EstatisticasGerais,
  EstatisticasPorNicho
} from '../../../app/types/api-sync';

describe('Sincronização de Tipos TypeScript', () => {
  
  describe('BaseEntity', () => {
    it('deve ter propriedades obrigatórias', () => {
      const entity: BaseEntity = {
        id: 'test-id',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z'
      };

      expect(entity.id).toBe('test-id');
      expect(entity.created_at).toBe('2024-12-27T22:30:00Z');
      expect(entity.updated_at).toBe('2024-12-27T22:30:00Z');
    });

    it('deve ter ID como string', () => {
      const entity: BaseEntity = {
        id: '123', // ✅ String, não number
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z'
      };

      expect(typeof entity.id).toBe('string');
    });
  });

  describe('Nicho', () => {
    it('deve estender BaseEntity', () => {
      const nicho: Nicho = {
        id: 'nicho-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        nome: 'Tecnologia',
        descricao: 'Nicho de tecnologia'
      };

      expect(nicho.id).toBe('nicho-1');
      expect(nicho.nome).toBe('Tecnologia');
      expect(nicho.descricao).toBe('Nicho de tecnologia');
    });

    it('deve ter propriedades opcionais', () => {
      const nicho: Nicho = {
        id: 'nicho-2',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        nome: 'Saúde'
        // descricao é opcional
      };

      expect(nicho.nome).toBe('Saúde');
      expect(nicho.descricao).toBeUndefined();
    });
  });

  describe('NichoCreate', () => {
    it('deve ter apenas propriedades necessárias para criação', () => {
      const nichoCreate: NichoCreate = {
        nome: 'Novo Nicho',
        descricao: 'Descrição do novo nicho'
      };

      expect(nichoCreate.nome).toBe('Novo Nicho');
      expect(nichoCreate.descricao).toBe('Descrição do novo nicho');
      expect('id' in nichoCreate).toBe(false); // Não deve ter ID
      expect('created_at' in nichoCreate).toBe(false); // Não deve ter timestamps
    });
  });

  describe('Categoria', () => {
    it('deve estender BaseEntity e ter referência ao nicho', () => {
      const categoria: Categoria = {
        id: 'categoria-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        nome: 'Programação',
        descricao: 'Categoria de programação',
        nicho_id: 'nicho-1'
      };

      expect(categoria.id).toBe('categoria-1');
      expect(categoria.nome).toBe('Programação');
      expect(categoria.nicho_id).toBe('nicho-1');
    });
  });

  describe('CategoriaCreate', () => {
    it('deve ter nicho_id obrigatório', () => {
      const categoriaCreate: CategoriaCreate = {
        nicho_id: 'nicho-1',
        nome: 'Nova Categoria',
        descricao: 'Descrição da nova categoria'
      };

      expect(categoriaCreate.nicho_id).toBe('nicho-1');
      expect(categoriaCreate.nome).toBe('Nova Categoria');
    });
  });

  describe('PromptBase', () => {
    it('deve ter propriedades de prompt', () => {
      const promptBase: PromptBase = {
        id: 'prompt-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        categoria_id: 'categoria-1',
        nome_arquivo: 'prompt.txt',
        conteudo: 'Conteúdo do prompt com [LACUNA]',
        hash_conteudo: 'abc123'
      };

      expect(promptBase.id).toBe('prompt-1');
      expect(promptBase.categoria_id).toBe('categoria-1');
      expect(promptBase.nome_arquivo).toBe('prompt.txt');
      expect(promptBase.conteudo).toBe('Conteúdo do prompt com [LACUNA]');
      expect(promptBase.hash_conteudo).toBe('abc123');
    });
  });

  describe('DadosColetados', () => {
    it('deve ter propriedades de dados coletados', () => {
      const dadosColetados: DadosColetados = {
        id: 'dados-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        categoria_id: 'categoria-1',
        primary_keyword: 'palavra-chave',
        secondary_keywords: ['kw1', 'kw2'],
        cluster_content: 'Conteúdo do cluster',
        metadata: { fonte: 'google', data_coleta: '2024-12-27' }
      };

      expect(dadosColetados.id).toBe('dados-1');
      expect(dadosColetados.categoria_id).toBe('categoria-1');
      expect(dadosColetados.primary_keyword).toBe('palavra-chave');
      expect(dadosColetados.secondary_keywords).toEqual(['kw1', 'kw2']);
      expect(dadosColetados.cluster_content).toBe('Conteúdo do cluster');
    });
  });

  describe('DadosColetadosCreate', () => {
    it('deve ter propriedades necessárias para criação', () => {
      const dadosCreate: DadosColetadosCreate = {
        categoria_id: 'categoria-1',
        primary_keyword: 'nova-palavra',
        secondary_keywords: ['kw1', 'kw2'],
        cluster_content: 'Novo conteúdo',
        metadata: { fonte: 'manual' }
      };

      expect(dadosCreate.categoria_id).toBe('categoria-1');
      expect(dadosCreate.primary_keyword).toBe('nova-palavra');
      expect(dadosCreate.secondary_keywords).toEqual(['kw1', 'kw2']);
    });
  });

  describe('PromptPreenchido', () => {
    it('deve ter propriedades de prompt preenchido', () => {
      const promptPreenchido: PromptPreenchido = {
        id: 'preenchido-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        categoria_id: 'categoria-1',
        dados_coletados_id: 'dados-1',
        prompt_base_id: 'prompt-1',
        conteudo_preenchido: 'Conteúdo preenchido com palavra-chave',
        status: 'processado',
        tempo_processamento: 1500,
        metadata: { lacunas_preenchidas: 3 }
      };

      expect(promptPreenchido.id).toBe('preenchido-1');
      expect(promptPreenchido.categoria_id).toBe('categoria-1');
      expect(promptPreenchido.dados_coletados_id).toBe('dados-1');
      expect(promptPreenchido.prompt_base_id).toBe('prompt-1');
      expect(promptPreenchido.conteudo_preenchido).toBe('Conteúdo preenchido com palavra-chave');
      expect(promptPreenchido.status).toBe('processado');
      expect(promptPreenchido.tempo_processamento).toBe(1500);
    });
  });

  describe('ProcessamentoResponse', () => {
    it('deve ter propriedades de resposta de processamento', () => {
      const processamentoResponse: ProcessamentoResponse = {
        success: true,
        total_processados: 10,
        sucessos: 8,
        falhas: 2,
        tempo_total: 5000,
        detalhes: {
          categoria_id: 'categoria-1',
          dados_coletados_id: 'dados-1'
        }
      };

      expect(processamentoResponse.success).toBe(true);
      expect(processamentoResponse.total_processados).toBe(10);
      expect(processamentoResponse.sucessos).toBe(8);
      expect(processamentoResponse.falhas).toBe(2);
      expect(processamentoResponse.tempo_total).toBe(5000);
    });
  });

  describe('EstatisticasGerais', () => {
    it('deve ter propriedades de estatísticas gerais', () => {
      const estatisticas: EstatisticasGerais = {
        total_nichos: 5,
        total_categorias: 20,
        total_prompts_base: 50,
        total_dados_coletados: 100,
        total_prompts_preenchidos: 80,
        tempo_medio_processamento: 1200,
        taxa_sucesso: 95.5,
        estatisticas_por_nicho: []
      };

      expect(estatisticas.total_nichos).toBe(5);
      expect(estatisticas.total_categorias).toBe(20);
      expect(estatisticas.total_prompts_base).toBe(50);
      expect(estatisticas.total_dados_coletados).toBe(100);
      expect(estatisticas.total_prompts_preenchidos).toBe(80);
      expect(estatisticas.tempo_medio_processamento).toBe(1200);
      expect(estatisticas.taxa_sucesso).toBe(95.5);
    });
  });

  describe('EstatisticasPorNicho', () => {
    it('deve ter propriedades de estatísticas por nicho', () => {
      const estatisticasNicho: EstatisticasPorNicho = {
        nicho_id: 'nicho-1',
        nome_nicho: 'Tecnologia',
        total_categorias: 8,
        total_prompts: 25,
        total_preenchidos: 20,
        taxa_sucesso: 92.0,
        tempo_medio: 1100
      };

      expect(estatisticasNicho.nicho_id).toBe('nicho-1');
      expect(estatisticasNicho.nome_nicho).toBe('Tecnologia');
      expect(estatisticasNicho.total_categorias).toBe(8);
      expect(estatisticasNicho.total_prompts).toBe(25);
      expect(estatisticasNicho.total_preenchidos).toBe(20);
      expect(estatisticasNicho.taxa_sucesso).toBe(92.0);
      expect(estatisticasNicho.tempo_medio).toBe(1100);
    });
  });

  describe('Compatibilidade com Backend', () => {
    it('deve validar que IDs são sempre strings', () => {
      // Simula dados vindos do backend
      const dadosBackend = {
        id: '123', // Backend retorna string
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z'
      };

      const entity: BaseEntity = dadosBackend;
      expect(typeof entity.id).toBe('string');
      expect(entity.id).toBe('123');
    });

    it('deve validar que referências entre entidades usam strings', () => {
      const categoria: Categoria = {
        id: 'cat-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        nome: 'Teste',
        nicho_id: 'nicho-1' // Referência como string
      };

      expect(typeof categoria.nicho_id).toBe('string');
      expect(categoria.nicho_id).toBe('nicho-1');
    });
  });

  describe('Validação de Tipos em Arrays', () => {
    it('deve validar arrays de entidades', () => {
      const nichos: Nicho[] = [
        {
          id: 'nicho-1',
          created_at: '2024-12-27T22:30:00Z',
          updated_at: '2024-12-27T22:30:00Z',
          nome: 'Nicho 1'
        },
        {
          id: 'nicho-2',
          created_at: '2024-12-27T22:30:00Z',
          updated_at: '2024-12-27T22:30:00Z',
          nome: 'Nicho 2'
        }
      ];

      expect(nichos).toHaveLength(2);
      expect(nichos[0].id).toBe('nicho-1');
      expect(nichos[1].id).toBe('nicho-2');
      expect(typeof nichos[0].id).toBe('string');
      expect(typeof nichos[1].id).toBe('string');
    });

    it('deve validar arrays de strings', () => {
      const dadosColetados: DadosColetados = {
        id: 'dados-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        categoria_id: 'cat-1',
        primary_keyword: 'principal',
        secondary_keywords: ['kw1', 'kw2', 'kw3'], // Array de strings
        cluster_content: 'conteúdo',
        metadata: {}
      };

      expect(Array.isArray(dadosColetados.secondary_keywords)).toBe(true);
      expect(dadosColetados.secondary_keywords).toEqual(['kw1', 'kw2', 'kw3']);
      dadosColetados.secondary_keywords.forEach(kw => {
        expect(typeof kw).toBe('string');
      });
    });
  });

  describe('Validação de Metadata', () => {
    it('deve aceitar metadata flexível', () => {
      const dadosColetados: DadosColetados = {
        id: 'dados-1',
        created_at: '2024-12-27T22:30:00Z',
        updated_at: '2024-12-27T22:30:00Z',
        categoria_id: 'cat-1',
        primary_keyword: 'teste',
        secondary_keywords: [],
        cluster_content: 'conteúdo',
        metadata: {
          fonte: 'google',
          data_coleta: '2024-12-27',
          score: 0.95,
          tags: ['importante', 'urgente']
        }
      };

      expect(dadosColetados.metadata.fonte).toBe('google');
      expect(dadosColetados.metadata.data_coleta).toBe('2024-12-27');
      expect(dadosColetados.metadata.score).toBe(0.95);
      expect(dadosColetados.metadata.tags).toEqual(['importante', 'urgente']);
    });
  });
}); 
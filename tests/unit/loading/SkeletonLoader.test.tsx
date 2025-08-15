/**
 * SkeletonLoader.test.tsx
 * 
 * Testes unitários para o componente SkeletonLoader
 * 
 * Tracing ID: TEST_LOADING_20250127_002
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 3.5
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { 
  Skeleton, 
  SkeletonGroup, 
  TableSkeleton, 
  CardSkeleton, 
  FormSkeleton, 
  ListSkeleton, 
  DashboardSkeleton,
  useSkeleton,
  SkeletonType 
} from '../../../app/components/loading/SkeletonLoader';

describe('SkeletonLoader Component', () => {
  describe('Skeleton Component', () => {
    describe('Renderização Básica', () => {
      it('deve renderizar com configurações padrão', () => {
        render(<Skeleton />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toBeInTheDocument();
        expect(skeleton).toHaveClass('bg-gray-200', 'dark:bg-gray-700', 'animate-pulse', 'rounded');
      });

      it('deve renderizar com tipo específico', () => {
        render(<Skeleton type="title" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-6', 'w-3/4');
      });

      it('deve renderizar com classes customizadas', () => {
        render(<Skeleton className="custom-class" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('custom-class');
      });

      it('deve renderizar com largura e altura customizadas', () => {
        render(<Skeleton width={200} height={100} />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveStyle({ width: '200px', height: '100px' });
      });

      it('deve renderizar com largura e altura como strings', () => {
        render(<Skeleton width="50%" height="2rem" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveStyle({ width: '50%', height: '2rem' });
      });
    });

    describe('Tipos de Skeleton', () => {
      it('deve renderizar skeleton de texto', () => {
        render(<Skeleton type="text" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-4', 'w-full');
      });

      it('deve renderizar skeleton de título', () => {
        render(<Skeleton type="title" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-6', 'w-3/4');
      });

      it('deve renderizar skeleton de parágrafo', () => {
        render(<Skeleton type="paragraph" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-4', 'w-full');
      });

      it('deve renderizar skeleton de avatar', () => {
        render(<Skeleton type="avatar" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-10', 'w-10', 'rounded-full');
      });

      it('deve renderizar skeleton de botão', () => {
        render(<Skeleton type="button" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-10', 'w-24');
      });

      it('deve renderizar skeleton de input', () => {
        render(<Skeleton type="input" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-10', 'w-full');
      });

      it('deve renderizar skeleton de card', () => {
        render(<Skeleton type="card" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-32', 'w-full');
      });

      it('deve renderizar skeleton de linha de tabela', () => {
        render(<Skeleton type="table-row" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-12', 'w-full');
      });

      it('deve renderizar skeleton de célula de tabela', () => {
        render(<Skeleton type="table-cell" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-6', 'w-full');
      });

      it('deve renderizar skeleton de item de lista', () => {
        render(<Skeleton type="list-item" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-16', 'w-full');
      });

      it('deve renderizar skeleton de imagem', () => {
        render(<Skeleton type="image" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-48', 'w-full');
      });

      it('deve renderizar skeleton de badge', () => {
        render(<Skeleton type="badge" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-6', 'w-16');
      });

      it('deve renderizar skeleton de progresso', () => {
        render(<Skeleton type="progress" />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('h-2', 'w-full');
      });
    });

    describe('Múltiplas Linhas', () => {
      it('deve renderizar múltiplas linhas', () => {
        render(<Skeleton lines={3} />);
        
        const skeletons = screen.getAllByTestId('skeleton');
        expect(skeletons).toHaveLength(3);
      });

      it('deve aplicar espaçamento entre linhas', () => {
        render(<Skeleton lines={2} />);
        
        const container = screen.getByTestId('skeleton-container');
        expect(container).toHaveClass('space-y-2');
      });

      it('deve usar tipo especificado para todas as linhas', () => {
        render(<Skeleton type="title" lines={3} />);
        
        const skeletons = screen.getAllByTestId('skeleton');
        skeletons.forEach(skeleton => {
          expect(skeleton).toHaveClass('h-6', 'w-3/4');
        });
      });
    });

    describe('Animações', () => {
      it('deve aplicar animação quando animated é true', () => {
        render(<Skeleton animated={true} />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('animate-pulse');
      });

      it('deve não aplicar animação quando animated é false', () => {
        render(<Skeleton animated={false} />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).not.toHaveClass('animate-pulse');
      });
    });

    describe('Bordas Arredondadas', () => {
      it('deve aplicar bordas arredondadas quando rounded é true', () => {
        render(<Skeleton rounded={true} />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).toHaveClass('rounded');
      });

      it('deve não aplicar bordas arredondadas quando rounded é false', () => {
        render(<Skeleton rounded={false} />);
        
        const skeleton = screen.getByTestId('skeleton');
        expect(skeleton).not.toHaveClass('rounded');
      });
    });
  });

  describe('SkeletonGroup Component', () => {
    it('deve renderizar grupo de skeletons', () => {
      render(
        <SkeletonGroup>
          <Skeleton type="title" />
          <Skeleton type="paragraph" />
          <Skeleton type="button" />
        </SkeletonGroup>
      );
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(3);
    });

    it('deve aplicar espaçamento entre skeletons', () => {
      render(
        <SkeletonGroup>
          <Skeleton type="title" />
          <Skeleton type="paragraph" />
        </SkeletonGroup>
      );
      
      const group = screen.getByTestId('skeleton-group');
      expect(group).toHaveClass('space-y-4');
    });

    it('deve aplicar classes customizadas ao grupo', () => {
      render(
        <SkeletonGroup className="custom-group">
          <Skeleton type="title" />
        </SkeletonGroup>
      );
      
      const group = screen.getByTestId('skeleton-group');
      expect(group).toHaveClass('custom-group');
    });

    it('deve propagar animação para todos os skeletons filhos', () => {
      render(
        <SkeletonGroup animated={false}>
          <Skeleton type="title" />
          <Skeleton type="paragraph" />
        </SkeletonGroup>
      );
      
      const skeletons = screen.getAllByTestId('skeleton');
      skeletons.forEach(skeleton => {
        expect(skeleton).not.toHaveClass('animate-pulse');
      });
    });
  });

  describe('TableSkeleton Component', () => {
    it('deve renderizar skeleton de tabela com configurações padrão', () => {
      render(<TableSkeleton />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(25); // 5 linhas + 1 header = 6, 4 colunas = 24 + 1 extra
    });

    it('deve renderizar skeleton de tabela com configurações customizadas', () => {
      render(<TableSkeleton rows={3} columns={2} />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(8); // 3 linhas + 1 header = 4, 2 colunas = 8
    });

    it('deve aplicar classes customizadas', () => {
      render(<TableSkeleton className="custom-table" />);
      
      const container = screen.getByTestId('table-skeleton');
      expect(container).toHaveClass('custom-table');
    });

    it('deve renderizar header e linhas separadamente', () => {
      render(<TableSkeleton rows={2} columns={3} />);
      
      const headerSkeletons = screen.getAllByTestId('skeleton').slice(0, 3);
      const rowSkeletons = screen.getAllByTestId('skeleton').slice(3);
      
      expect(headerSkeletons).toHaveLength(3);
      expect(rowSkeletons).toHaveLength(6); // 2 linhas * 3 colunas
    });
  });

  describe('CardSkeleton Component', () => {
    it('deve renderizar skeleton de card com configurações padrão', () => {
      render(<CardSkeleton />);
      
      expect(screen.getByTestId('card-skeleton')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-avatar')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-title')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-paragraph')).toBeInTheDocument();
    });

    it('deve renderizar skeleton de card sem avatar', () => {
      render(<CardSkeleton showAvatar={false} />);
      
      expect(screen.queryByTestId('skeleton-avatar')).not.toBeInTheDocument();
    });

    it('deve renderizar skeleton de card sem ações', () => {
      render(<CardSkeleton showActions={false} />);
      
      expect(screen.queryByTestId('skeleton-actions')).not.toBeInTheDocument();
    });

    it('deve aplicar classes customizadas', () => {
      render(<CardSkeleton className="custom-card" />);
      
      const card = screen.getByTestId('card-skeleton');
      expect(card).toHaveClass('custom-card');
    });
  });

  describe('FormSkeleton Component', () => {
    it('deve renderizar skeleton de formulário com configurações padrão', () => {
      render(<FormSkeleton />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(8); // 4 campos * 2 (label + input)
    });

    it('deve renderizar skeleton de formulário com número customizado de campos', () => {
      render(<FormSkeleton fields={2} />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(4); // 2 campos * 2 (label + input)
    });

    it('deve aplicar classes customizadas', () => {
      render(<FormSkeleton className="custom-form" />);
      
      const form = screen.getByTestId('form-skeleton');
      expect(form).toHaveClass('custom-form');
    });
  });

  describe('ListSkeleton Component', () => {
    it('deve renderizar skeleton de lista com configurações padrão', () => {
      render(<ListSkeleton />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(5); // 5 itens padrão
    });

    it('deve renderizar skeleton de lista com número customizado de itens', () => {
      render(<ListSkeleton items={3} />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(3);
    });

    it('deve aplicar classes customizadas', () => {
      render(<ListSkeleton className="custom-list" />);
      
      const list = screen.getByTestId('list-skeleton');
      expect(list).toHaveClass('custom-list');
    });
  });

  describe('DashboardSkeleton Component', () => {
    it('deve renderizar skeleton de dashboard', () => {
      render(<DashboardSkeleton />);
      
      expect(screen.getByTestId('dashboard-skeleton')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-header')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-stats')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-chart')).toBeInTheDocument();
      expect(screen.getByTestId('skeleton-table')).toBeInTheDocument();
    });

    it('deve aplicar classes customizadas', () => {
      render(<DashboardSkeleton className="custom-dashboard" />);
      
      const dashboard = screen.getByTestId('dashboard-skeleton');
      expect(dashboard).toHaveClass('custom-dashboard');
    });
  });

  describe('Hook useSkeleton', () => {
    it('deve retornar skeleton quando loading é true', () => {
      const TestComponent = () => {
        const result = useSkeleton(
          true,
          <div>Conteúdo real</div>,
          <Skeleton type="text" />
        );
        
        return <div data-testid="result">{result}</div>;
      };
      
      render(<TestComponent />);
      
      expect(screen.getByTestId('skeleton')).toBeInTheDocument();
      expect(screen.queryByText('Conteúdo real')).not.toBeInTheDocument();
    });

    it('deve retornar conteúdo real quando loading é false', () => {
      const TestComponent = () => {
        const result = useSkeleton(
          false,
          <div>Conteúdo real</div>,
          <Skeleton type="text" />
        );
        
        return <div data-testid="result">{result}</div>;
      };
      
      render(<TestComponent />);
      
      expect(screen.queryByTestId('skeleton')).not.toBeInTheDocument();
      expect(screen.getByText('Conteúdo real')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter role apropriado para skeletons', () => {
      render(<Skeleton />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveAttribute('role', 'status');
      expect(skeleton).toHaveAttribute('aria-label', 'Carregando...');
    });

    it('deve ter aria-hidden quando não animado', () => {
      render(<Skeleton animated={false} />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveAttribute('aria-hidden', 'true');
    });

    it('deve ter aria-live quando animado', () => {
      render(<Skeleton animated={true} />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Performance', () => {
    it('deve memoizar renderização para evitar re-renders desnecessários', () => {
      const { rerender } = render(<Skeleton type="text" />);
      
      const initialRender = screen.getByTestId('skeleton');
      
      rerender(<Skeleton type="text" />);
      
      const reRender = screen.getByTestId('skeleton');
      expect(reRender).toBe(initialRender);
    });

    it('deve aplicar animações apenas quando necessário', () => {
      const { rerender } = render(<Skeleton animated={true} />);
      expect(screen.getByTestId('skeleton')).toHaveClass('animate-pulse');
      
      rerender(<Skeleton animated={false} />);
      expect(screen.getByTestId('skeleton')).not.toHaveClass('animate-pulse');
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com zero linhas', () => {
      render(<Skeleton lines={0} />);
      
      const skeletons = screen.queryAllByTestId('skeleton');
      expect(skeletons).toHaveLength(0);
    });

    it('deve lidar com muitas linhas', () => {
      render(<Skeleton lines={100} />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons).toHaveLength(100);
    });

    it('deve lidar com valores negativos de largura/altura', () => {
      render(<Skeleton width={-100} height={-50} />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveStyle({ width: '0px', height: '0px' });
    });

    it('deve lidar com valores muito grandes de largura/altura', () => {
      render(<Skeleton width={9999} height={9999} />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveStyle({ width: '9999px', height: '9999px' });
    });

    it('deve lidar com strings vazias para largura/altura', () => {
      render(<Skeleton width="" height="" />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveStyle({ width: '', height: '' });
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', () => {
      render(<Skeleton />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveClass('dark:bg-gray-700');
    });

    it('deve integrar com sistema de classes utilitárias', () => {
      render(<Skeleton className="custom-skeleton" />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveClass('custom-skeleton');
    });

    it('deve integrar com sistema de animações', () => {
      render(<Skeleton animated={true} />);
      
      const skeleton = screen.getByTestId('skeleton');
      expect(skeleton).toHaveClass('animate-pulse');
    });
  });
}); 
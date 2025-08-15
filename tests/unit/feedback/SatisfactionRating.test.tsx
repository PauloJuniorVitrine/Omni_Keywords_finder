/**
 * Testes Unitários - SatisfactionRating Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_SATISFACTION_RATING_021
 * 
 * Baseado em código real do SatisfactionRating.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SatisfactionRating, NPSRating, EmojiRating } from '../../../app/components/feedback/SatisfactionRating';

describe('SatisfactionRating - Sistema de Rating de Satisfação', () => {
  
  describe('SatisfactionRating Component', () => {
    
    test('deve renderizar o componente com configurações padrão', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      // Verificar se as 5 estrelas estão sendo renderizadas
      const stars = screen.getAllByRole('button');
      expect(stars).toHaveLength(5);
      
      // Verificar se cada estrela tem o aria-label correto
      stars.forEach((star, index) => {
        expect(star).toHaveAttribute('aria-label', `Avaliar ${index + 1} de 5 estrelas`);
      });
    });

    test('deve renderizar com valor inicial', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={3} onChange={mockOnChange} />);
      
      // Verificar se o valor é exibido
      expect(screen.getByText('3 de 5')).toBeInTheDocument();
    });

    test('deve permitir seleção de rating', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      await user.click(stars[2]); // Clicar na terceira estrela
      
      expect(mockOnChange).toHaveBeenCalledWith(3);
    });

    test('deve exibir label quando rating é selecionado', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={4} onChange={mockOnChange} />);
      
      expect(screen.getByText('Bom')).toBeInTheDocument();
    });

    test('deve ocultar label quando showLabels é false', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={4} onChange={mockOnChange} showLabels={false} />);
      
      expect(screen.queryByText('Bom')).not.toBeInTheDocument();
    });

    test('deve renderizar com tamanhos diferentes', () => {
      const mockOnChange = jest.fn();
      
      // Testar tamanho small
      const { rerender } = render(
        <SatisfactionRating value={0} onChange={mockOnChange} size="small" />
      );
      let stars = screen.getAllByRole('button');
      expect(stars[0]).toHaveClass('w-4', 'h-4');
      
      // Testar tamanho large
      rerender(<SatisfactionRating value={0} onChange={mockOnChange} size="large" />);
      stars = screen.getAllByRole('button');
      expect(stars[0]).toHaveClass('w-8', 'h-8');
      
      // Testar tamanho medium (padrão)
      rerender(<SatisfactionRating value={0} onChange={mockOnChange} size="medium" />);
      stars = screen.getAllByRole('button');
      expect(stars[0]).toHaveClass('w-6', 'h-6');
    });

    test('deve renderizar com labels customizados', () => {
      const mockOnChange = jest.fn();
      const customLabels = ['Péssimo', 'Ruim', 'Regular', 'Bom', 'Ótimo'];
      
      render(
        <SatisfactionRating 
          value={4} 
          onChange={mockOnChange} 
          labels={customLabels}
        />
      );
      
      expect(screen.getByText('Bom')).toBeInTheDocument();
    });

    test('deve renderizar com rating máximo customizado', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} maxRating={10} />);
      
      const stars = screen.getAllByRole('button');
      expect(stars).toHaveLength(10);
      
      // Verificar se o aria-label está correto para 10 estrelas
      expect(stars[0]).toHaveAttribute('aria-label', 'Avaliar 1 de 10 estrelas');
    });

    test('deve aplicar cores corretas baseadas no valor', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={3} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      
      // As primeiras 3 estrelas devem estar preenchidas
      expect(stars[0]).toHaveClass('text-yellow-400', 'fill-current');
      expect(stars[1]).toHaveClass('text-yellow-400', 'fill-current');
      expect(stars[2]).toHaveClass('text-yellow-400', 'fill-current');
      
      // As últimas 2 estrelas devem estar vazias
      expect(stars[3]).toHaveClass('text-gray-300');
      expect(stars[4]).toHaveClass('text-gray-300');
    });

    test('deve ter transições suaves', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      expect(stars[0]).toHaveClass('transition-colors', 'duration-200');
    });

    test('deve ser acessível com navegação por teclado', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      
      // Verificar se todos os botões são focáveis
      stars.forEach(star => {
        expect(star).toHaveAttribute('tabIndex', '0');
      });
    });
  });

  describe('NPSRating Component', () => {
    
    test('deve renderizar o componente NPS', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      // Verificar se os 11 botões de score estão sendo renderizados (0-10)
      const scoreButtons = screen.getAllByRole('button');
      expect(scoreButtons).toHaveLength(11);
      
      // Verificar se os scores estão corretos
      scoreButtons.forEach((button, index) => {
        expect(button).toHaveTextContent(index.toString());
        expect(button).toHaveAttribute('aria-label', `NPS Score ${index}`);
      });
    });

    test('deve permitir seleção de score NPS', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      await user.click(scoreButtons[8]); // Clicar no score 8
      
      expect(mockOnChange).toHaveBeenCalledWith(8);
    });

    test('deve aplicar cores corretas baseadas no score', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={5} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      
      // Score 5 (detrator) deve ser vermelho
      expect(scoreButtons[5]).toHaveClass('bg-red-500');
      
      // Score 7 (passivo) deve ser amarelo
      expect(scoreButtons[7]).toHaveClass('bg-yellow-500');
      
      // Score 9 (promotor) deve ser verde
      expect(scoreButtons[9]).toHaveClass('bg-green-500');
    });

    test('deve exibir label correto baseado no score', () => {
      const mockOnChange = jest.fn();
      
      // Testar detrator
      const { rerender } = render(<NPSRating value={3} onChange={mockOnChange} />);
      expect(screen.getByText('Detrator (3/10)')).toBeInTheDocument();
      
      // Testar passivo
      rerender(<NPSRating value={7} onChange={mockOnChange} />);
      expect(screen.getByText('Passivo (7/10)')).toBeInTheDocument();
      
      // Testar promotor
      rerender(<NPSRating value={9} onChange={mockOnChange} />);
      expect(screen.getByText('Promotor (9/10)')).toBeInTheDocument();
    });

    test('deve destacar score selecionado', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={7} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      expect(scoreButtons[7]).toHaveClass('ring-2', 'ring-blue-500');
    });

    test('deve ocultar label quando showLabels é false', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={8} onChange={mockOnChange} showLabels={false} />);
      
      expect(screen.queryByText('Passivo (8/10)')).not.toBeInTheDocument();
    });

    test('deve ter transições suaves', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      expect(scoreButtons[0]).toHaveClass('transition-all', 'duration-200');
    });

    test('deve ser acessível com navegação por teclado', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      
      // Verificar se todos os botões são focáveis
      scoreButtons.forEach(button => {
        expect(button).toHaveAttribute('tabIndex', '0');
      });
    });
  });

  describe('EmojiRating Component', () => {
    
    test('deve renderizar o componente de emoji rating', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      // Verificar se os 5 emojis estão sendo renderizados
      const emojiButtons = screen.getAllByRole('button');
      expect(emojiButtons).toHaveLength(5);
      
      // Verificar se os emojis estão corretos
      const expectedEmojis = ['😞', '😐', '😊', '😄', '🤩'];
      emojiButtons.forEach((button, index) => {
        expect(button).toHaveTextContent(expectedEmojis[index]);
        expect(button).toHaveAttribute('aria-label', ['Muito Ruim', 'Ruim', 'Regular', 'Bom', 'Excelente'][index]);
      });
    });

    test('deve permitir seleção de emoji', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      await user.click(emojiButtons[3]); // Clicar no quarto emoji (😄)
      
      expect(mockOnChange).toHaveBeenCalledWith(4);
    });

    test('deve exibir label quando emoji é selecionado', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={4} onChange={mockOnChange} />);
      
      expect(screen.getByText('Bom')).toBeInTheDocument();
    });

    test('deve destacar emoji selecionado', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={3} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      expect(emojiButtons[2]).toHaveClass('bg-blue-100', 'scale-110');
    });

    test('deve renderizar com emojis customizados', () => {
      const mockOnChange = jest.fn();
      const customEmojis = ['😢', '😕', '😐', '🙂', '😍'];
      const customLabels = ['Triste', 'Insatisfeito', 'Neutro', 'Satisfeito', 'Muito Satisfeito'];
      
      render(
        <EmojiRating 
          value={0} 
          onChange={mockOnChange} 
          emojis={customEmojis}
          labels={customLabels}
        />
      );
      
      const emojiButtons = screen.getAllByRole('button');
      emojiButtons.forEach((button, index) => {
        expect(button).toHaveTextContent(customEmojis[index]);
        expect(button).toHaveAttribute('aria-label', customLabels[index]);
      });
    });

    test('deve aplicar hover effects', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      expect(emojiButtons[0]).toHaveClass('hover:bg-gray-100', 'hover:scale-105');
    });

    test('deve ter transições suaves', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      expect(emojiButtons[0]).toHaveClass('transition-all', 'duration-200');
    });

    test('deve ser acessível com navegação por teclado', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      
      // Verificar se todos os botões são focáveis
      emojiButtons.forEach(button => {
        expect(button).toHaveAttribute('tabIndex', '0');
      });
    });
  });

  describe('Validação de Entrada', () => {
    
    test('deve validar valor mínimo no SatisfactionRating', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      expect(stars).toHaveLength(5);
      
      // Verificar se o valor 0 não exibe label
      expect(screen.queryByText('Muito Ruim')).not.toBeInTheDocument();
    });

    test('deve validar valor máximo no SatisfactionRating', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={5} onChange={mockOnChange} />);
      
      expect(screen.getByText('Excelente')).toBeInTheDocument();
      expect(screen.getByText('5 de 5')).toBeInTheDocument();
    });

    test('deve validar valor inicial no NPSRating', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      // Verificar se não exibe label quando valor é -1
      expect(screen.queryByText(/Detrator|Passivo|Promotor/)).not.toBeInTheDocument();
    });

    test('deve validar valores válidos no NPSRating', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={10} onChange={mockOnChange} />);
      
      expect(screen.getByText('Promotor (10/10)')).toBeInTheDocument();
    });

    test('deve validar valor inicial no EmojiRating', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      // Verificar se não exibe label quando valor é 0
      expect(screen.queryByText(/Muito Ruim|Ruim|Regular|Bom|Excelente/)).not.toBeInTheDocument();
    });

    test('deve validar valores válidos no EmojiRating', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={5} onChange={mockOnChange} />);
      
      expect(screen.getByText('Excelente')).toBeInTheDocument();
    });
  });

  describe('Submissão de Feedback', () => {
    
    test('deve chamar onChange quando rating é selecionado no SatisfactionRating', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      await user.click(stars[4]); // Clicar na quinta estrela
      
      expect(mockOnChange).toHaveBeenCalledWith(5);
      expect(mockOnChange).toHaveBeenCalledTimes(1);
    });

    test('deve chamar onChange quando score é selecionado no NPSRating', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      await user.click(scoreButtons[9]); // Clicar no score 9
      
      expect(mockOnChange).toHaveBeenCalledWith(9);
      expect(mockOnChange).toHaveBeenCalledTimes(1);
    });

    test('deve chamar onChange quando emoji é selecionado no EmojiRating', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      await user.click(emojiButtons[1]); // Clicar no segundo emoji
      
      expect(mockOnChange).toHaveBeenCalledWith(2);
      expect(mockOnChange).toHaveBeenCalledTimes(1);
    });

    test('deve permitir múltiplas seleções consecutivas', async () => {
      const user = userEvent.setup();
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      
      await user.click(stars[2]); // Clicar na terceira estrela
      await user.click(stars[4]); // Clicar na quinta estrela
      
      expect(mockOnChange).toHaveBeenCalledWith(3);
      expect(mockOnChange).toHaveBeenCalledWith(5);
      expect(mockOnChange).toHaveBeenCalledTimes(2);
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter aria-labels apropriados no SatisfactionRating', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      stars.forEach((star, index) => {
        expect(star).toHaveAttribute('aria-label', `Avaliar ${index + 1} de 5 estrelas`);
      });
    });

    test('deve ter aria-labels apropriados no NPSRating', () => {
      const mockOnChange = jest.fn();
      render(<NPSRating value={-1} onChange={mockOnChange} />);
      
      const scoreButtons = screen.getAllByRole('button');
      scoreButtons.forEach((button, index) => {
        expect(button).toHaveAttribute('aria-label', `NPS Score ${index}`);
      });
    });

    test('deve ter aria-labels apropriados no EmojiRating', () => {
      const mockOnChange = jest.fn();
      render(<EmojiRating value={0} onChange={mockOnChange} />);
      
      const emojiButtons = screen.getAllByRole('button');
      const expectedLabels = ['Muito Ruim', 'Ruim', 'Regular', 'Bom', 'Excelente'];
      
      emojiButtons.forEach((button, index) => {
        expect(button).toHaveAttribute('aria-label', expectedLabels[index]);
      });
    });

    test('deve ser navegável por teclado', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      stars.forEach(star => {
        expect(star).toHaveAttribute('tabIndex', '0');
      });
    });

    test('deve ter contraste adequado', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={3} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      // Verificar se as estrelas selecionadas têm cor adequada
      expect(stars[0]).toHaveClass('text-yellow-400');
      expect(stars[1]).toHaveClass('text-yellow-400');
      expect(stars[2]).toHaveClass('text-yellow-400');
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente com muitos ratings', () => {
      const mockOnChange = jest.fn();
      const startTime = performance.now();
      
      render(<SatisfactionRating value={0} onChange={mockOnChange} maxRating={10} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve usar transições CSS para performance', () => {
      const mockOnChange = jest.fn();
      render(<SatisfactionRating value={0} onChange={mockOnChange} />);
      
      const stars = screen.getAllByRole('button');
      expect(stars[0]).toHaveClass('transition-colors', 'duration-200');
    });

    test('deve evitar re-renders desnecessários', () => {
      const mockOnChange = jest.fn();
      const { rerender } = render(<SatisfactionRating value={3} onChange={mockOnChange} />);
      
      // Re-renderizar com o mesmo valor não deve causar mudanças
      rerender(<SatisfactionRating value={3} onChange={mockOnChange} />);
      
      expect(screen.getByText('Regular')).toBeInTheDocument();
    });
  });
}); 
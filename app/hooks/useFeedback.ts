import { useState, useCallback } from 'react';

interface FeedbackData {
  rating: number;
  feedback: string;
  category: string;
  email?: string;
  timestamp: string;
}

interface UseFeedbackReturn {
  isModalOpen: boolean;
  isLoading: boolean;
  error: string | null;
  openModal: () => void;
  closeModal: () => void;
  submitFeedback: (data: FeedbackData) => Promise<void>;
}

export const useFeedback = (): UseFeedbackReturn => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const openModal = useCallback(() => {
    setIsModalOpen(true);
    setError(null);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setError(null);
  }, []);

  const submitFeedback = useCallback(async (data: FeedbackData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Erro ao enviar feedback');
      }

      // Feedback enviado com sucesso
      closeModal();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }, [closeModal]);

  return {
    isModalOpen,
    isLoading,
    error,
    openModal,
    closeModal,
    submitFeedback,
  };
}; 
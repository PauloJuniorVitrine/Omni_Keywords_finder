export interface Feedback {
  id: string;
  rating: number;
  feedback: string;
  category: FeedbackCategory;
  email?: string;
  userId?: string;
  timestamp: string;
  status: FeedbackStatus;
  tags?: string[];
  metadata?: Record<string, any>;
}

export type FeedbackCategory = 
  | 'general'
  | 'bug'
  | 'feature'
  | 'improvement'
  | 'performance'
  | 'ui_ux'
  | 'api'
  | 'integration';

export type FeedbackStatus = 
  | 'pending'
  | 'reviewed'
  | 'in_progress'
  | 'resolved'
  | 'closed';

export interface FeedbackSubmission {
  rating: number;
  feedback: string;
  category: FeedbackCategory;
  email?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
  feedbackId?: string;
  error?: string;
}

export interface FeedbackFilters {
  category?: FeedbackCategory;
  status?: FeedbackStatus;
  rating?: number;
  dateFrom?: string;
  dateTo?: string;
  userId?: string;
}

export interface FeedbackStats {
  total: number;
  averageRating: number;
  byCategory: Record<FeedbackCategory, number>;
  byStatus: Record<FeedbackStatus, number>;
  recentSubmissions: number;
} 
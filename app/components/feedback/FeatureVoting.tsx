import React, { useState } from 'react';

interface FeatureVotingProps {
  featureId: string;
  currentVotes: number;
  userVoted: boolean;
  onVote: (featureId: string, vote: boolean) => void;
}

export const FeatureVoting: React.FC<FeatureVotingProps> = ({
  featureId,
  currentVotes,
  userVoted,
  onVote
}) => {
  const [votes, setVotes] = useState(currentVotes);
  const [hasVoted, setHasVoted] = useState(userVoted);

  const handleVote = () => {
    if (!hasVoted) {
      setVotes(votes + 1);
      setHasVoted(true);
      onVote(featureId, true);
    } else {
      setVotes(votes - 1);
      setHasVoted(false);
      onVote(featureId, false);
    }
  };

  return (
    <div className="feature-voting">
      <button
        onClick={handleVote}
        className={`vote-button ${hasVoted ? 'voted' : ''}`}
        aria-label={hasVoted ? 'Remover voto' : 'Votar nesta funcionalidade'}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
        <span className="vote-count">{votes}</span>
      </button>
      
      <span className="vote-label">
        {hasVoted ? 'Votado' : 'Votar'}
      </span>
    </div>
  );
};

interface FeatureRequestListProps {
  features: Array<{
    id: string;
    title: string;
    description: string;
    category: string;
    priority: string;
    votes: number;
    status: string;
    createdAt: string;
  }>;
  onVote: (featureId: string, vote: boolean) => void;
  userVotes: Set<string>;
}

export const FeatureRequestList: React.FC<FeatureRequestListProps> = ({
  features,
  onVote,
  userVotes
}) => {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('votes');

  const filteredFeatures = features.filter(feature => {
    if (filter === 'all') return true;
    return feature.category === filter;
  });

  const sortedFeatures = [...filteredFeatures].sort((a, b) => {
    switch (sortBy) {
      case 'votes':
        return b.votes - a.votes;
      case 'date':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      case 'priority':
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority as keyof typeof priorityOrder] - 
               priorityOrder[a.priority as keyof typeof priorityOrder];
      default:
        return 0;
    }
  });

  return (
    <div className="feature-request-list">
      <div className="feature-list-controls">
        <div className="filter-controls">
          <label htmlFor="category-filter">Filtrar por categoria:</label>
          <select
            id="category-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="form-select"
          >
            <option value="all">Todas</option>
            <option value="general">Geral</option>
            <option value="analytics">Analytics</option>
            <option value="integration">Integração</option>
            <option value="ui_ux">Interface</option>
            <option value="api">API</option>
            <option value="export">Exportação</option>
            <option value="automation">Automação</option>
            <option value="reporting">Relatórios</option>
          </select>
        </div>

        <div className="sort-controls">
          <label htmlFor="sort-by">Ordenar por:</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="form-select"
          >
            <option value="votes">Mais votadas</option>
            <option value="date">Mais recentes</option>
            <option value="priority">Prioridade</option>
          </select>
        </div>
      </div>

      <div className="feature-list">
        {sortedFeatures.map(feature => (
          <div key={feature.id} className="feature-item">
            <div className="feature-header">
              <h3 className="feature-title">{feature.title}</h3>
              <div className="feature-meta">
                <span className={`priority-badge ${feature.priority}`}>
                  {feature.priority}
                </span>
                <span className={`status-badge ${feature.status}`}>
                  {feature.status}
                </span>
              </div>
            </div>
            
            <p className="feature-description">{feature.description}</p>
            
            <div className="feature-footer">
              <FeatureVoting
                featureId={feature.id}
                currentVotes={feature.votes}
                userVoted={userVotes.has(feature.id)}
                onVote={onVote}
              />
              
              <div className="feature-info">
                <span className="feature-category">{feature.category}</span>
                <span className="feature-date">
                  {new Date(feature.createdAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 
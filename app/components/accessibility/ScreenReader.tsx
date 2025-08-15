import React, { useState, useEffect, useRef } from 'react';

export interface ScreenReaderProps {
  children?: React.ReactNode;
  announcement?: string;
  priority?: 'polite' | 'assertive';
  role?: string;
  ariaLabel?: string;
  ariaDescribedBy?: string;
  ariaLabelledBy?: string;
  ariaHidden?: boolean;
  ariaLive?: 'off' | 'polite' | 'assertive';
  className?: string;
}

export interface ScreenReaderAnnouncement {
  id: string;
  message: string;
  priority: 'polite' | 'assertive';
  timestamp: number;
}

export const ScreenReader: React.FC<ScreenReaderProps> = ({
  children,
  announcement,
  priority = 'polite',
  role,
  ariaLabel,
  ariaDescribedBy,
  ariaLabelledBy,
  ariaHidden = false,
  ariaLive = 'polite',
  className = ''
}) => {
  const [announcements, setAnnouncements] = useState<ScreenReaderAnnouncement[]>([]);
  const liveRegionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (announcement) {
      const newAnnouncement: ScreenReaderAnnouncement = {
        id: `announcement-${Date.now()}`,
        message: announcement,
        priority,
        timestamp: Date.now()
      };

      setAnnouncements(prev => [...prev, newAnnouncement]);

      // Clean up old announcements after 5 seconds
      setTimeout(() => {
        setAnnouncements(prev => prev.filter(a => a.id !== newAnnouncement.id));
      }, 5000);
    }
  }, [announcement, priority]);

  const ariaProps = {
    role,
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedBy,
    'aria-labelledby': ariaLabelledBy,
    'aria-hidden': ariaHidden,
    'aria-live': ariaLive
  };

  return (
    <>
      {/* Live region for announcements */}
      <div
        ref={liveRegionRef}
        aria-live={priority}
        aria-atomic="true"
        className="sr-only"
        style={{
          position: 'absolute',
          left: '-10000px',
          width: '1px',
          height: '1px',
          overflow: 'hidden'
        }}
      >
        {announcements.map(announcement => (
          <div key={announcement.id}>
            {announcement.message}
          </div>
        ))}
      </div>

      {/* Main content */}
      <div
        {...ariaProps}
        className={className}
      >
        {children}
      </div>
    </>
  );
};

// Screen Reader Announcement Component
export interface ScreenReaderAnnouncementProps {
  message: string;
  priority?: 'polite' | 'assertive';
  delay?: number;
  onAnnounce?: () => void;
}

export const ScreenReaderAnnouncement: React.FC<ScreenReaderAnnouncementProps> = ({
  message,
  priority = 'polite',
  delay = 0,
  onAnnounce
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
      onAnnounce?.();
    }, delay);

    return () => clearTimeout(timer);
  }, [delay, onAnnounce]);

  if (!isVisible) return null;

  return (
    <div
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
      style={{
        position: 'absolute',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden'
      }}
    >
      {message}
    </div>
  );
};

// Screen Reader Navigation Component
export interface ScreenReaderNavigationProps {
  landmarks?: Array<{
    id: string;
    label: string;
    type: 'main' | 'navigation' | 'banner' | 'contentinfo' | 'complementary' | 'search';
  }>;
  onNavigate?: (landmarkId: string) => void;
}

export const ScreenReaderNavigation: React.FC<ScreenReaderNavigationProps> = ({
  landmarks = [],
  onNavigate
}) => {
  const [currentLandmark, setCurrentLandmark] = useState<string>('');

  const handleLandmarkNavigation = (landmarkId: string) => {
    setCurrentLandmark(landmarkId);
    onNavigate?.(landmarkId);
  };

  return (
    <nav aria-label="Screen reader navigation" className="sr-only">
      <h2>Landmarks</h2>
      <ul>
        {landmarks.map(landmark => (
          <li key={landmark.id}>
            <button
              onClick={() => handleLandmarkNavigation(landmark.id)}
              aria-current={currentLandmark === landmark.id ? 'true' : undefined}
            >
              {landmark.label} ({landmark.type})
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

// Screen Reader Skip Link Component
export interface ScreenReaderSkipLinkProps {
  targetId: string;
  label?: string;
  className?: string;
}

export const ScreenReaderSkipLink: React.FC<ScreenReaderSkipLinkProps> = ({
  targetId,
  label = 'Skip to main content',
  className = ''
}) => {
  const handleSkip = () => {
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView();
    }
  };

  return (
    <a
      href={`#${targetId}`}
      onClick={handleSkip}
      className={`skip-link ${className}`}
      style={{
        position: 'absolute',
        top: '-40px',
        left: '6px',
        zIndex: 1000,
        padding: '8px 16px',
        backgroundColor: '#000',
        color: '#fff',
        textDecoration: 'none',
        borderRadius: '4px',
        fontSize: '14px',
        fontWeight: 'bold'
      }}
      onFocus={(e) => {
        e.currentTarget.style.top = '6px';
      }}
      onBlur={(e) => {
        e.currentTarget.style.top = '-40px';
      }}
    >
      {label}
    </a>
  );
};

// Screen Reader Status Component
export interface ScreenReaderStatusProps {
  status: string;
  isVisible?: boolean;
  priority?: 'polite' | 'assertive';
}

export const ScreenReaderStatus: React.FC<ScreenReaderStatusProps> = ({
  status,
  isVisible = true,
  priority = 'polite'
}) => {
  if (!isVisible) return null;

  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {status}
    </div>
  );
};

// Screen Reader Instructions Component
export interface ScreenReaderInstructionsProps {
  instructions: string;
  elementId?: string;
  className?: string;
}

export const ScreenReaderInstructions: React.FC<ScreenReaderInstructionsProps> = ({
  instructions,
  elementId,
  className = ''
}) => {
  return (
    <div
      id={elementId}
      className={`sr-instructions ${className}`}
      style={{
        position: 'absolute',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden'
      }}
    >
      {instructions}
    </div>
  );
}; 
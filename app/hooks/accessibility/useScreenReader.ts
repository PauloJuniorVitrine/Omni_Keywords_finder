import { useState, useEffect, useRef, useCallback } from 'react';

export interface ScreenReaderAnnouncement {
  id: string;
  message: string;
  priority: 'polite' | 'assertive';
  timestamp: number;
}

export interface ScreenReaderLandmark {
  id: string;
  label: string;
  type: 'main' | 'navigation' | 'banner' | 'contentinfo' | 'complementary' | 'search' | 'form' | 'region';
}

export interface UseScreenReaderReturn {
  announcements: ScreenReaderAnnouncement[];
  landmarks: ScreenReaderLandmark[];
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  announceImmediately: (message: string) => void;
  addLandmark: (landmark: ScreenReaderLandmark) => void;
  removeLandmark: (id: string) => void;
  navigateToLandmark: (id: string) => void;
  clearAnnouncements: () => void;
  isScreenReaderActive: boolean;
  liveRegionRef: React.RefObject<HTMLDivElement>;
}

export const useScreenReader = (): UseScreenReaderReturn => {
  const [announcements, setAnnouncements] = useState<ScreenReaderAnnouncement[]>([]);
  const [landmarks, setLandmarks] = useState<ScreenReaderLandmark[]>([]);
  const [isScreenReaderActive, setIsScreenReaderActive] = useState(false);
  const liveRegionRef = useRef<HTMLDivElement>(null);

  // Detect screen reader usage
  const detectScreenReader = useCallback(() => {
    // Check for common screen reader indicators
    const indicators = [
      'speechSynthesis' in window,
      'webkitSpeechSynthesis' in window,
      navigator.userAgent.includes('NVDA'),
      navigator.userAgent.includes('JAWS'),
      navigator.userAgent.includes('VoiceOver'),
      navigator.userAgent.includes('TalkBack')
    ];

    const hasScreenReader = indicators.some(Boolean);
    setIsScreenReaderActive(hasScreenReader);
  }, []);

  useEffect(() => {
    detectScreenReader();
  }, [detectScreenReader]);

  // Announce message
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement: ScreenReaderAnnouncement = {
      id: `announcement-${Date.now()}-${Math.random()}`,
      message,
      priority,
      timestamp: Date.now()
    };

    setAnnouncements(prev => [...prev, announcement]);

    // Clean up old announcements after 5 seconds
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(a => a.id !== announcement.id));
    }, 5000);

    // Use speech synthesis if available
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      speechSynthesis.speak(utterance);
    }
  }, []);

  // Announce immediately (assertive)
  const announceImmediately = useCallback((message: string) => {
    announce(message, 'assertive');
  }, [announce]);

  // Landmark management
  const addLandmark = useCallback((landmark: ScreenReaderLandmark) => {
    setLandmarks(prev => {
      const existing = prev.find(l => l.id === landmark.id);
      if (existing) {
        return prev.map(l => l.id === landmark.id ? landmark : l);
      }
      return [...prev, landmark];
    });
  }, []);

  const removeLandmark = useCallback((id: string) => {
    setLandmarks(prev => prev.filter(l => l.id !== id));
  }, []);

  const navigateToLandmark = useCallback((id: string) => {
    const landmark = landmarks.find(l => l.id === id);
    if (landmark) {
      const element = document.getElementById(id);
      if (element) {
        element.focus();
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        announce(`Navigated to ${landmark.label}`);
      }
    }
  }, [landmarks, announce]);

  const clearAnnouncements = useCallback(() => {
    setAnnouncements([]);
  }, []);

  return {
    announcements,
    landmarks,
    announce,
    announceImmediately,
    addLandmark,
    removeLandmark,
    navigateToLandmark,
    clearAnnouncements,
    isScreenReaderActive,
    liveRegionRef
  };
};

// Specialized screen reader hooks
export const useScreenReaderAnnouncements = () => {
  const [announcements, setAnnouncements] = useState<ScreenReaderAnnouncement[]>([]);

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement: ScreenReaderAnnouncement = {
      id: `announcement-${Date.now()}`,
      message,
      priority,
      timestamp: Date.now()
    };

    setAnnouncements(prev => [...prev, announcement]);

    // Clean up after 5 seconds
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(a => a.id !== announcement.id));
    }, 5000);
  }, []);

  const clearAnnouncements = useCallback(() => {
    setAnnouncements([]);
  }, []);

  return {
    announcements,
    announce,
    clearAnnouncements
  };
};

export const useScreenReaderNavigation = () => {
  const [currentSection, setCurrentSection] = useState<string>('');
  const [sections, setSections] = useState<Array<{ id: string; label: string; element: HTMLElement }>>([]);

  const registerSection = useCallback((id: string, label: string, element: HTMLElement) => {
    setSections(prev => {
      const existing = prev.find(s => s.id === id);
      if (existing) {
        return prev.map(s => s.id === id ? { id, label, element } : s);
      }
      return [...prev, { id, label, element }];
    });
  }, []);

  const unregisterSection = useCallback((id: string) => {
    setSections(prev => prev.filter(s => s.id !== id));
  }, []);

  const navigateToSection = useCallback((id: string) => {
    const section = sections.find(s => s.id === id);
    if (section) {
      section.element.focus();
      section.element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setCurrentSection(id);
    }
  }, [sections]);

  const navigateNext = useCallback(() => {
    const currentIndex = sections.findIndex(s => s.id === currentSection);
    const nextIndex = currentIndex < sections.length - 1 ? currentIndex + 1 : 0;
    navigateToSection(sections[nextIndex].id);
  }, [sections, currentSection, navigateToSection]);

  const navigatePrevious = useCallback(() => {
    const currentIndex = sections.findIndex(s => s.id === currentSection);
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : sections.length - 1;
    navigateToSection(sections[prevIndex].id);
  }, [sections, currentSection, navigateToSection]);

  return {
    currentSection,
    sections,
    registerSection,
    unregisterSection,
    navigateToSection,
    navigateNext,
    navigatePrevious
  };
};

export const useScreenReaderStatus = () => {
  const [status, setStatus] = useState<string>('');
  const statusRef = useRef<HTMLDivElement>(null);

  const updateStatus = useCallback((newStatus: string) => {
    setStatus(newStatus);
    
    // Update live region
    if (statusRef.current) {
      statusRef.current.textContent = newStatus;
    }
  }, []);

  const clearStatus = useCallback(() => {
    setStatus('');
    if (statusRef.current) {
      statusRef.current.textContent = '';
    }
  }, []);

  return {
    status,
    updateStatus,
    clearStatus,
    statusRef
  };
};

// Screen reader utilities
export const screenReaderUtils = {
  // Create accessible label
  createLabel: (text: string, elementId?: string) => {
    if (elementId) {
      return { 'aria-labelledby': elementId };
    }
    return { 'aria-label': text };
  },

  // Create accessible description
  createDescription: (text: string, elementId?: string) => {
    if (elementId) {
      return { 'aria-describedby': elementId };
    }
    return { 'aria-label': text };
  },

  // Create live region
  createLiveRegion: (priority: 'polite' | 'assertive' = 'polite') => ({
    'aria-live': priority,
    'aria-atomic': 'true'
  }),

  // Create landmark
  createLandmark: (type: 'main' | 'navigation' | 'banner' | 'contentinfo' | 'complementary' | 'search') => ({
    role: type
  }),

  // Create skip link
  createSkipLink: (targetId: string, label: string = 'Skip to main content') => ({
    href: `#${targetId}`,
    'aria-label': label
  }),

  // Create focus indicator
  createFocusIndicator: () => ({
    tabIndex: 0,
    onFocus: (e: React.FocusEvent) => {
      e.currentTarget.style.outline = '2px solid #2196f3';
      e.currentTarget.style.outlineOffset = '2px';
    },
    onBlur: (e: React.FocusEvent) => {
      e.currentTarget.style.outline = '';
      e.currentTarget.style.outlineOffset = '';
    }
  })
}; 
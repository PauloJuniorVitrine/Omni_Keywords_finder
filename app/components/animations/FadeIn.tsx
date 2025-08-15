import React, { useState, useEffect, useRef } from 'react';

export interface FadeInProps {
  children: React.ReactNode;
  duration?: number;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'none';
  distance?: number;
  easing?: 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'linear';
  threshold?: number;
  trigger?: 'onMount' | 'onScroll' | 'onHover' | 'onClick' | 'manual';
  className?: string;
  style?: React.CSSProperties;
  onAnimationStart?: () => void;
  onAnimationEnd?: () => void;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  duration = 600,
  delay = 0,
  direction = 'none',
  distance = 20,
  easing = 'ease-out',
  threshold = 0.1,
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const getInitialTransform = () => {
    switch (direction) {
      case 'up':
        return `translateY(${distance}px)`;
      case 'down':
        return `translateY(-${distance}px)`;
      case 'left':
        return `translateX(${distance}px)`;
      case 'right':
        return `translateX(-${distance}px)`;
      default:
        return 'none';
    }
  };

  const getFinalTransform = () => {
    return direction === 'none' ? 'none' : 'translate(0, 0)';
  };

  const startAnimation = () => {
    if (isVisible || isAnimating) return;
    
    setIsAnimating(true);
    onAnimationStart?.();
    
    setTimeout(() => {
      setIsVisible(true);
      setIsAnimating(false);
      onAnimationEnd?.();
    }, delay);
  };

  // Handle different triggers
  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  useEffect(() => {
    if (trigger === 'onScroll' && elementRef.current) {
      observerRef.current = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            startAnimation();
            observerRef.current?.disconnect();
          }
        },
        { threshold }
      );

      observerRef.current.observe(elementRef.current);

      return () => {
        observerRef.current?.disconnect();
      };
    }
  }, [trigger, threshold]);

  const handleHover = () => {
    if (trigger === 'onHover' && !isVisible) {
      startAnimation();
    }
  };

  const handleClick = () => {
    if (trigger === 'onClick') {
      startAnimation();
    }
  };

  const animationStyles: React.CSSProperties = {
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? getFinalTransform() : getInitialTransform(),
    transition: `opacity ${duration}ms ${easing}, transform ${duration}ms ${easing}`,
    transitionDelay: `${delay}ms`,
    ...style
  };

  return (
    <div
      ref={elementRef}
      className={className}
      style={animationStyles}
      onMouseEnter={handleHover}
      onClick={handleClick}
    >
      {children}
    </div>
  );
};

// Variant components for common use cases
export const FadeInUp: React.FC<Omit<FadeInProps, 'direction'> & { distance?: number }> = (props) => (
  <FadeIn {...props} direction="up" />
);

export const FadeInDown: React.FC<Omit<FadeInProps, 'direction'> & { distance?: number }> = (props) => (
  <FadeIn {...props} direction="down" />
);

export const FadeInLeft: React.FC<Omit<FadeInProps, 'direction'> & { distance?: number }> = (props) => (
  <FadeIn {...props} direction="left" />
);

export const FadeInRight: React.FC<Omit<FadeInProps, 'direction'> & { distance?: number }> = (props) => (
  <FadeIn {...props} direction="right" />
);

// Staggered animation for multiple children
export interface StaggeredFadeInProps extends Omit<FadeInProps, 'children'> {
  children: React.ReactNode[];
  staggerDelay?: number;
}

export const StaggeredFadeIn: React.FC<StaggeredFadeInProps> = ({
  children,
  staggerDelay = 100,
  ...props
}) => {
  return (
    <>
      {children.map((child, index) => (
        <FadeIn
          key={index}
          {...props}
          delay={props.delay + (index * staggerDelay)}
        >
          {child}
        </FadeIn>
      ))}
    </>
  );
}; 
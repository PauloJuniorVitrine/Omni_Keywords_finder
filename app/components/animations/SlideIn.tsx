import React, { useState, useEffect, useRef } from 'react';

export interface SlideInProps {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
  duration?: number;
  delay?: number;
  easing?: 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'linear' | 'bounce' | 'elastic';
  threshold?: number;
  trigger?: 'onMount' | 'onScroll' | 'onHover' | 'onClick' | 'manual';
  className?: string;
  style?: React.CSSProperties;
  onAnimationStart?: () => void;
  onAnimationEnd?: () => void;
}

export const SlideIn: React.FC<SlideInProps> = ({
  children,
  direction = 'up',
  distance = 50,
  duration = 800,
  delay = 0,
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
        return 'translateY(50px)';
    }
  };

  const getEasingFunction = () => {
    switch (easing) {
      case 'bounce':
        return 'cubic-bezier(0.68, -0.55, 0.265, 1.55)';
      case 'elastic':
        return 'cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      default:
        return easing;
    }
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
    transform: isVisible ? 'translate(0, 0)' : getInitialTransform(),
    transition: `opacity ${duration}ms ${getEasingFunction()}, transform ${duration}ms ${getEasingFunction()}`,
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

// Direction-specific components
export const SlideInUp: React.FC<Omit<SlideInProps, 'direction'> & { distance?: number }> = (props) => (
  <SlideIn {...props} direction="up" />
);

export const SlideInDown: React.FC<Omit<SlideInProps, 'direction'> & { distance?: number }> = (props) => (
  <SlideIn {...props} direction="down" />
);

export const SlideInLeft: React.FC<Omit<SlideInProps, 'direction'> & { distance?: number }> = (props) => (
  <SlideIn {...props} direction="left" />
);

export const SlideInRight: React.FC<Omit<SlideInProps, 'direction'> & { distance?: number }> = (props) => (
  <SlideIn {...props} direction="right" />
);

// Staggered slide animation
export interface StaggeredSlideInProps extends Omit<SlideInProps, 'children'> {
  children: React.ReactNode[];
  staggerDelay?: number;
}

export const StaggeredSlideIn: React.FC<StaggeredSlideInProps> = ({
  children,
  staggerDelay = 150,
  ...props
}) => {
  return (
    <>
      {children.map((child, index) => (
        <SlideIn
          key={index}
          {...props}
          delay={props.delay + (index * staggerDelay)}
        >
          {child}
        </SlideIn>
      ))}
    </>
  );
};

// Slide in from corners
export const SlideInFromTopLeft: React.FC<Omit<SlideInProps, 'direction' | 'children'> & { children: React.ReactNode }> = (props) => (
  <div
    style={{
      transform: props.style?.transform || 'translate(-50px, -50px)',
      transition: `transform ${props.duration || 800}ms ${props.easing || 'ease-out'}`,
      opacity: 0,
      animation: 'slideInFromTopLeft 0.8s ease-out forwards'
    }}
    className={props.className}
  >
    {props.children}
  </div>
);

export const SlideInFromTopRight: React.FC<Omit<SlideInProps, 'direction' | 'children'> & { children: React.ReactNode }> = (props) => (
  <div
    style={{
      transform: props.style?.transform || 'translate(50px, -50px)',
      transition: `transform ${props.duration || 800}ms ${props.easing || 'ease-out'}`,
      opacity: 0,
      animation: 'slideInFromTopRight 0.8s ease-out forwards'
    }}
    className={props.className}
  >
    {props.children}
  </div>
);

export const SlideInFromBottomLeft: React.FC<Omit<SlideInProps, 'direction' | 'children'> & { children: React.ReactNode }> = (props) => (
  <div
    style={{
      transform: props.style?.transform || 'translate(-50px, 50px)',
      transition: `transform ${props.duration || 800}ms ${props.easing || 'ease-out'}`,
      opacity: 0,
      animation: 'slideInFromBottomLeft 0.8s ease-out forwards'
    }}
    className={props.className}
  >
    {props.children}
  </div>
);

export const SlideInFromBottomRight: React.FC<Omit<SlideInProps, 'direction' | 'children'> & { children: React.ReactNode }> = (props) => (
  <div
    style={{
      transform: props.style?.transform || 'translate(50px, 50px)',
      transition: `transform ${props.duration || 800}ms ${props.easing || 'ease-out'}`,
      opacity: 0,
      animation: 'slideInFromBottomRight 0.8s ease-out forwards'
    }}
    className={props.className}
  >
    {props.children}
  </div>
); 
import React, { useState, useEffect, useRef } from 'react';

export interface BounceProps {
  children: React.ReactNode;
  type?: 'bounce' | 'bounceIn' | 'bounceOut' | 'bounceInUp' | 'bounceInDown' | 'bounceInLeft' | 'bounceInRight';
  duration?: number;
  delay?: number;
  repeat?: number | 'infinite';
  trigger?: 'onMount' | 'onHover' | 'onClick' | 'manual';
  className?: string;
  style?: React.CSSProperties;
  onAnimationStart?: () => void;
  onAnimationEnd?: () => void;
}

export const Bounce: React.FC<BounceProps> = ({
  children,
  type = 'bounce',
  duration = 1000,
  delay = 0,
  repeat = 1,
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const getKeyframes = () => {
    switch (type) {
      case 'bounce':
        return `
          @keyframes bounce {
            0%, 20%, 53%, 80%, 100% {
              transform: translate3d(0, 0, 0);
            }
            40%, 43% {
              transform: translate3d(0, -30px, 0);
            }
            70% {
              transform: translate3d(0, -15px, 0);
            }
            90% {
              transform: translate3d(0, -4px, 0);
            }
          }
        `;
      
      case 'bounceIn':
        return `
          @keyframes bounceIn {
            0% {
              opacity: 0;
              transform: scale(0.3);
            }
            50% {
              opacity: 1;
              transform: scale(1.05);
            }
            70% {
              transform: scale(0.9);
            }
            100% {
              opacity: 1;
              transform: scale(1);
            }
          }
        `;
      
      case 'bounceOut':
        return `
          @keyframes bounceOut {
            0% {
              transform: scale(1);
            }
            25% {
              transform: scale(0.95);
            }
            50% {
              opacity: 1;
              transform: scale(1.1);
            }
            100% {
              opacity: 0;
              transform: scale(0.3);
            }
          }
        `;
      
      case 'bounceInUp':
        return `
          @keyframes bounceInUp {
            0% {
              opacity: 0;
              transform: translate3d(0, 3000px, 0);
            }
            60% {
              opacity: 1;
              transform: translate3d(0, -20px, 0);
            }
            80% {
              transform: translate3d(0, 10px, 0);
            }
            100% {
              opacity: 1;
              transform: translate3d(0, 0, 0);
            }
          }
        `;
      
      case 'bounceInDown':
        return `
          @keyframes bounceInDown {
            0% {
              opacity: 0;
              transform: translate3d(0, -3000px, 0);
            }
            60% {
              opacity: 1;
              transform: translate3d(0, 25px, 0);
            }
            75% {
              transform: translate3d(0, -10px, 0);
            }
            90% {
              transform: translate3d(0, 5px, 0);
            }
            100% {
              opacity: 1;
              transform: translate3d(0, 0, 0);
            }
          }
        `;
      
      case 'bounceInLeft':
        return `
          @keyframes bounceInLeft {
            0% {
              opacity: 0;
              transform: translate3d(-3000px, 0, 0);
            }
            60% {
              opacity: 1;
              transform: translate3d(25px, 0, 0);
            }
            75% {
              transform: translate3d(-10px, 0, 0);
            }
            90% {
              transform: translate3d(5px, 0, 0);
            }
            100% {
              opacity: 1;
              transform: translate3d(0, 0, 0);
            }
          }
        `;
      
      case 'bounceInRight':
        return `
          @keyframes bounceInRight {
            0% {
              opacity: 0;
              transform: translate3d(3000px, 0, 0);
            }
            60% {
              opacity: 1;
              transform: translate3d(-25px, 0, 0);
            }
            75% {
              transform: translate3d(10px, 0, 0);
            }
            90% {
              transform: translate3d(-5px, 0, 0);
            }
            100% {
              opacity: 1;
              transform: translate3d(0, 0, 0);
            }
          }
        `;
      
      default:
        return '';
    }
  };

  const startAnimation = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setIsVisible(true);
    onAnimationStart?.();
    
    if (repeat !== 'infinite') {
      setTimeout(() => {
        setIsAnimating(false);
        if (type === 'bounceOut') {
          setIsVisible(false);
        }
        onAnimationEnd?.();
      }, delay + (duration * repeat));
    }
  };

  const stopAnimation = () => {
    setIsAnimating(false);
    onAnimationEnd?.();
  };

  // Handle different triggers
  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const handleHover = () => {
    if (trigger === 'onHover') {
      if (!isAnimating) {
        startAnimation();
      }
    }
  };

  const handleMouseLeave = () => {
    if (trigger === 'onHover' && repeat === 'infinite') {
      stopAnimation();
    }
  };

  const handleClick = () => {
    if (trigger === 'onClick') {
      startAnimation();
    }
  };

  const animationStyles: React.CSSProperties = {
    opacity: isVisible ? 1 : 0,
    animation: isAnimating 
      ? `${type} ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getKeyframes()}</style>
      <div
        ref={elementRef}
        className={className}
        style={animationStyles}
        onMouseEnter={handleHover}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      >
        {children}
      </div>
    </>
  );
};

// Type-specific components
export const BounceIn: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceIn" />
);

export const BounceOut: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceOut" />
);

export const BounceInUp: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceInUp" />
);

export const BounceInDown: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceInDown" />
);

export const BounceInLeft: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceInLeft" />
);

export const BounceInRight: React.FC<Omit<BounceProps, 'type'>> = (props) => (
  <Bounce {...props} type="bounceInRight" />
);

// Bounce with custom properties
export interface BounceCustomProps extends Omit<BounceProps, 'type'> {
  height?: number;
  stiffness?: number;
}

export const BounceCustom: React.FC<BounceCustomProps> = ({
  children,
  height = 30,
  stiffness = 0.8,
  duration = 1000,
  delay = 0,
  repeat = 1,
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getCustomBounceKeyframes = () => `
    @keyframes customBounce {
      0% {
        transform: translateY(0);
      }
      25% {
        transform: translateY(-${height}px);
      }
      50% {
        transform: translateY(-${height * stiffness}px);
      }
      75% {
        transform: translateY(-${height * 0.5}px);
      }
      100% {
        transform: translateY(0);
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    onAnimationStart?.();
  };

  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `customBounce ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getCustomBounceKeyframes()}</style>
      <div
        className={className}
        style={animationStyles}
        onMouseEnter={trigger === 'onHover' ? startAnimation : undefined}
        onClick={trigger === 'onClick' ? startAnimation : undefined}
      >
        {children}
      </div>
    </>
  );
}; 
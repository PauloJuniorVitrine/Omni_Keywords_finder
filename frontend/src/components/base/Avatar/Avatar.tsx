import React, { forwardRef, useState } from 'react';
import { cn } from '../../../utils/cn';

// Tipos específicos para o sistema Omni Keywords Finder
export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  shape?: 'circle' | 'square';
  status?: 'online' | 'offline' | 'away' | 'busy';
  fallback?: React.ReactNode;
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      className,
      src,
      alt,
      name,
      size = 'md',
      shape = 'circle',
      status,
      fallback,
      ...props
    },
    ref
  ) => {
    const [imageError, setImageError] = useState(false);

    // Design tokens específicos do Omni Keywords Finder
    const avatarSizes = {
      xs: 'w-6 h-6 text-xs',
      sm: 'w-8 h-8 text-sm',
      md: 'w-10 h-10 text-sm',
      lg: 'w-12 h-12 text-base',
      xl: 'w-16 h-16 text-lg',
      '2xl': 'w-20 h-20 text-xl'
    };

    const statusColors = {
      online: 'bg-green-400',
      offline: 'bg-gray-400',
      away: 'bg-yellow-400',
      busy: 'bg-red-400'
    };

    const statusSizes = {
      xs: 'w-1.5 h-1.5',
      sm: 'w-2 h-2',
      md: 'w-2.5 h-2.5',
      lg: 'w-3 h-3',
      xl: 'w-4 h-4',
      '2xl': 'w-5 h-5'
    };

    // Função para gerar iniciais do nome
    const getInitials = (name: string) => {
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2);
    };

    // Função para gerar cor baseada no nome
    const getColorFromName = (name: string) => {
      const colors = [
        'bg-red-500',
        'bg-blue-500',
        'bg-green-500',
        'bg-yellow-500',
        'bg-purple-500',
        'bg-pink-500',
        'bg-indigo-500',
        'bg-teal-500'
      ];
      
      const hash = name.split('').reduce((acc, char) => {
        return char.charCodeAt(0) + ((acc << 5) - acc);
      }, 0);
      
      return colors[Math.abs(hash) % colors.length];
    };

    const showImage = src && !imageError;
    const showFallback = !showImage && (fallback || name);

    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-block',
          avatarSizes[size],
          shape === 'circle' ? 'rounded-full' : 'rounded-lg',
          className
        )}
        {...props}
      >
        {showImage && (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className={cn(
              'w-full h-full object-cover',
              shape === 'circle' ? 'rounded-full' : 'rounded-lg'
            )}
            onError={() => setImageError(true)}
          />
        )}
        
        {showFallback && (
          <div
            className={cn(
              'w-full h-full flex items-center justify-center text-white font-medium',
              shape === 'circle' ? 'rounded-full' : 'rounded-lg',
              name ? getColorFromName(name) : 'bg-gray-500'
            )}
          >
            {fallback || (name && getInitials(name))}
          </div>
        )}
        
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0 block rounded-full ring-2 ring-white',
              statusColors[status],
              statusSizes[size]
            )}
            aria-label={`Status: ${status}`}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

// Componente Avatar Group para múltiplos avatares
export interface AvatarGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  avatars: Array<{
    src?: string;
    alt?: string;
    name?: string;
  }>;
  max?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  shape?: 'circle' | 'square';
}

export const AvatarGroup = forwardRef<HTMLDivElement, AvatarGroupProps>(
  (
    {
      className,
      avatars,
      max = 5,
      size = 'md',
      shape = 'circle',
      ...props
    },
    ref
  ) => {
    const visibleAvatars = avatars.slice(0, max);
    const hiddenCount = avatars.length - max;

    return (
      <div
        ref={ref}
        className={cn('flex -space-x-2', className)}
        {...props}
      >
        {visibleAvatars.map((avatar, index) => (
          <Avatar
            key={index}
            src={avatar.src}
            alt={avatar.alt}
            name={avatar.name}
            size={size}
            shape={shape}
            className="ring-2 ring-white"
          />
        ))}
        
        {hiddenCount > 0 && (
          <div
            className={cn(
              'flex items-center justify-center bg-gray-500 text-white font-medium ring-2 ring-white',
              shape === 'circle' ? 'rounded-full' : 'rounded-lg',
              size === 'xs' ? 'w-6 h-6 text-xs' :
              size === 'sm' ? 'w-8 h-8 text-sm' :
              size === 'md' ? 'w-10 h-10 text-sm' :
              size === 'lg' ? 'w-12 h-12 text-base' :
              size === 'xl' ? 'w-16 h-16 text-lg' :
              'w-20 h-20 text-xl'
            )}
          >
            +{hiddenCount}
          </div>
        )}
      </div>
    );
  }
);

AvatarGroup.displayName = 'AvatarGroup'; 
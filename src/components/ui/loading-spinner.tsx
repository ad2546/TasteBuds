import React from 'react';
import { Loader2 } from 'lucide-react';
import { colors } from '@/lib/design-tokens';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
  fullScreen?: boolean;
  message?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const colorClasses = {
  primary: `text-[${colors.primary[500]}]`,
  secondary: `text-[${colors.secondary[500]}]`,
  white: 'text-white',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  fullScreen = false,
  message,
}) => {
  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2
        className={`${sizeClasses[size]} ${colorClasses[color]} animate-spin`}
        aria-label="Loading"
      />
      {message && <p className={`text-sm ${colorClasses[color]} font-medium`}>{message}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        {spinner}
      </div>
    );
  }

  return spinner;
};

// Skeleton loader for content
export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string;
  height?: string;
  circle?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = 'w-full',
  height = 'h-4',
  circle = false,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`
        animate-pulse
        bg-[${colors.neutral[200]}]
        ${circle ? 'rounded-full' : 'rounded-lg'}
        ${width}
        ${height}
        ${className}
      `}
      style={{
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s infinite',
      }}
      {...props}
    />
  );
};

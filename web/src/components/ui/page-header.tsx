'use client'

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { colors } from '@/lib/design-tokens';

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  showBack?: boolean;
  variant?: 'gradient' | 'solid' | 'minimal';
  action?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  onBack,
  showBack = true,
  variant = 'gradient',
  action,
}) => {
  const router = useRouter();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  const variantStyles = {
    gradient: `
      bg-[${colors.primary[500]}]
      text-white
      px-4 pt-4 pb-8
    `,
    solid: `
      bg-white
      border-b border-[${colors.neutral[200]}]
      px-4 py-4
    `,
    minimal: `
      bg-transparent
      px-4 py-4
    `,
  };

  const textColor = variant === 'gradient' ? 'text-white' : `text-[${colors.neutral[900]}]`;
  const subtitleColor = variant === 'gradient' ? 'text-white/80' : `text-[${colors.neutral[600]}]`;

  return (
    <div className={variantStyles[variant]}>
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-4">
          {showBack && (
            <button
              onClick={handleBack}
              className={`
                w-10 h-10 rounded-full
                ${variant === 'gradient' ? 'bg-white/20' : `bg-[${colors.neutral[100]}]`}
                flex items-center justify-center
                hover:scale-110
                transition-transform
                duration-200
              `}
              aria-label="Go back"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}

          {action && <div className="ml-auto">{action}</div>}
        </div>

        <div className="text-center">
          <h1 className={`text-2xl font-bold ${textColor} mb-1`}>{title}</h1>
          {subtitle && <p className={`text-sm ${subtitleColor}`}>{subtitle}</p>}
        </div>
      </div>
    </div>
  );
};

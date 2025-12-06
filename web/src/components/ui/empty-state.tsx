import React from 'react';
import { LucideIcon } from 'lucide-react';
import { colors } from '@/lib/design-tokens';
import { Button } from './button';

export interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div
        className={`
          w-20 h-20 rounded-full
          bg-[${colors.primary[100]}]
          flex items-center justify-center
          mb-6
        `}
      >
        <Icon className={`w-10 h-10 text-[${colors.primary[500]}]`} aria-hidden="true" />
      </div>

      <h3 className={`text-xl font-bold text-[${colors.neutral[900]}] mb-2`}>{title}</h3>

      {description && (
        <p className={`text-[${colors.neutral[600]}] max-w-md mb-6`}>{description}</p>
      )}

      {(actionLabel || secondaryActionLabel) && (
        <div className="flex flex-col sm:flex-row gap-3">
          {actionLabel && onAction && (
            <Button onClick={onAction} variant="primary">
              {actionLabel}
            </Button>
          )}

          {secondaryActionLabel && onSecondaryAction && (
            <Button onClick={onSecondaryAction} variant="outline">
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

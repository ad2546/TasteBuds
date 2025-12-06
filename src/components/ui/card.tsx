import React from 'react';
import { colors, components, shadows, borderRadius } from '@/lib/design-tokens';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated' | 'gradient';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ children, variant = 'default', padding = 'md', hoverable = false, className = '', ...props }, ref) => {
    const baseStyles = `
      rounded-2xl
      transition-all duration-200
    `;

    const variantStyles = {
      default: `
        bg-white
        shadow-lg
      `,
      bordered: `
        bg-white
        border-2 border-[${colors.neutral[200]}]
      `,
      elevated: `
        bg-white
        shadow-xl
      `,
      gradient: `
        bg-white
        shadow-lg
      `,
    };

    const paddingStyles = {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    const hoverStyles = hoverable
      ? 'hover:shadow-2xl hover:scale-[1.02] cursor-pointer'
      : '';

    return (
      <div
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${paddingStyles[padding]} ${hoverStyles} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header Component
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ title, subtitle, action, className = '', ...props }) => {
  return (
    <div className={`flex items-start justify-between mb-4 ${className}`} {...props}>
      <div className="flex-1">
        <h3 className="text-xl font-bold text-[${colors.neutral[900]}]">{title}</h3>
        {subtitle && <p className="text-sm text-[${colors.neutral[600]}] mt-1">{subtitle}</p>}
      </div>
      {action && <div className="ml-4">{action}</div>}
    </div>
  );
};

// Card Content Component
export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className = '', ...props }) => {
  return (
    <div className={`${className}`} {...props}>
      {children}
    </div>
  );
};

// Card Footer Component
export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className = '', ...props }) => {
  return (
    <div className={`mt-6 pt-4 border-t border-[${colors.neutral[200]}] ${className}`} {...props}>
      {children}
    </div>
  );
};

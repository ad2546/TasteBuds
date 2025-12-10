import React from 'react';
import { Loader2 } from 'lucide-react';
import { colors, components, transitions } from '@/lib/design-tokens';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseStyles = `
      inline-flex items-center justify-center gap-2
      font-semibold rounded-xl
      transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
      active:scale-[0.98]
    `;

    const variantStyles = {
      primary: `
        bg-[${colors.primary[500]}] text-white
        hover:bg-[${colors.primary[600]}]
        focus:ring-[${colors.primary[500]}]
        shadow-md hover:shadow-lg
      `,
      secondary: `
        bg-[${colors.secondary[500]}] text-white
        hover:bg-[${colors.secondary[600]}]
        focus:ring-[${colors.secondary[500]}]
        shadow-md hover:shadow-lg
      `,
      outline: `
        border-2 border-[${colors.primary[500]}] text-[${colors.primary[500]}]
        hover:bg-[${colors.primary[50]}]
        focus:ring-[${colors.primary[500]}]
      `,
      ghost: `
        text-[${colors.neutral[700]}]
        hover:bg-[${colors.neutral[100]}]
        focus:ring-[${colors.neutral[400]}]
      `,
      gradient: `
        bg-[${colors.primary[500]}]
        text-white
        hover:shadow-xl hover:scale-[1.02]
        focus:ring-[${colors.primary[500]}]
        shadow-lg
      `,
    };

    const sizeStyles = {
      sm: `h-[${components.button.height.sm}] px-4 text-sm`,
      md: `h-[${components.button.height.md}] px-6 text-base`,
      lg: `h-[${components.button.height.lg}] px-8 text-lg`,
    };

    const widthStyle = fullWidth ? 'w-full' : '';

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyle} ${className}`}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" aria-label="Loading" />
            {loadingText && <span>{loadingText}</span>}
          </>
        ) : (
          <>
            {leftIcon && <span className="inline-flex">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="inline-flex">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

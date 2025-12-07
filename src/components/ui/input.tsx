import React, { forwardRef, useId } from 'react';
import { colors, components } from '@/lib/design-tokens';
import { AlertCircle } from 'lucide-react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  inputSize?: 'sm' | 'md' | 'lg';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      inputSize = 'md',
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id || generatedId;

    const baseStyles = `
      w-full
      px-4
      border-2
      rounded-xl
      transition-all duration-200
      focus:outline-none
      focus:ring-2
      focus:ring-offset-1
      disabled:opacity-50
      disabled:cursor-not-allowed
      disabled:bg-[${colors.neutral[100]}]
    `;

    const sizeStyles = {
      sm: `h-[${components.input.height.sm}] text-sm`,
      md: `h-[${components.input.height.md}] text-base`,
      lg: `h-[${components.input.height.lg}] text-lg`,
    };

    const stateStyles = error
      ? `
        border-[${colors.error}]
        text-[${colors.error}]
        focus:border-[${colors.error}]
        focus:ring-[${colors.error}]/20
      `
      : `
        border-[${colors.neutral[300]}]
        text-[${colors.neutral[900]}]
        focus:border-[${colors.primary[500]}]
        focus:ring-[${colors.primary[500]}]/20
        hover:border-[${colors.neutral[400]}]
      `;

    const iconPaddingLeft = leftIcon ? 'pl-12' : '';
    const iconPaddingRight = rightIcon ? 'pr-12' : '';

    return (
      <div className={`${fullWidth ? 'w-full' : ''}`}>
        {label && (
          <label
            htmlFor={inputId}
            className={`block text-sm font-semibold mb-2 ${
              error ? `text-[${colors.error}]` : `text-[${colors.neutral[700]}]`
            }`}
          >
            {label}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-[${colors.neutral[500]}]">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={`${baseStyles} ${sizeStyles[inputSize]} ${stateStyles} ${iconPaddingLeft} ${iconPaddingRight} ${className}`}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
            }
            {...props}
          />

          {rightIcon && !error && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-[${colors.neutral[500]}]">
              {rightIcon}
            </div>
          )}

          {error && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <AlertCircle className="w-5 h-5 text-[${colors.error}]" aria-hidden="true" />
            </div>
          )}
        </div>

        {error && (
          <p
            id={`${inputId}-error`}
            className="mt-2 text-sm text-[${colors.error}] flex items-center gap-1"
            role="alert"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${inputId}-helper`} className="mt-2 text-sm text-[${colors.neutral[600]}]">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

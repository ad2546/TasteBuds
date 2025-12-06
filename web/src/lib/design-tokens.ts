/**
 * Design Tokens - TasteSync Design System
 * Inspired by Yelp's bold, clean aesthetic with dating app warmth
 */

export const colors = {
  // Primary - Yelp Red with warmth
  primary: {
    50: '#FFE5E5',
    100: '#FFB8B8',
    200: '#FF8A8A',
    300: '#FF5C5C',
    400: '#FF3D3D',
    500: '#D32323', // Main Yelp Red
    600: '#C41200',
    700: '#A30F00',
    800: '#820C00',
    900: '#610900',
  },

  // Secondary - Warm Orange
  secondary: {
    50: '#FFF4E6',
    100: '#FFE0B2',
    200: '#FFCC80',
    300: '#FFB74D',
    400: '#FFA726',
    500: '#FFA94D',
    600: '#FF9800',
    700: '#F57C00',
    800: '#E65100',
    900: '#BF360C',
  },

  // Accent - Teal (for success, matches)
  accent: {
    50: '#E0F7F4',
    100: '#B2EBE4',
    200: '#80DED3',
    300: '#4DD1C1',
    400: '#26C6B4',
    500: '#4ECDC4',
    600: '#00B8A9',
    700: '#00A896',
    800: '#009688',
    900: '#00796B',
  },

  // Neutral - Clean grays
  neutral: {
    0: '#FFFFFF',
    50: '#F8F9FA',
    100: '#F1F3F5',
    200: '#E9ECEF',
    300: '#DEE2E6',
    400: '#CED4DA',
    500: '#ADB5BD',
    600: '#868E96',
    700: '#6C757D',
    800: '#495057',
    900: '#2C3E50',
    950: '#1A252F',
  },

  // Semantic colors
  success: '#51CF66',
  warning: '#FFD43B',
  error: '#FF6B6B',
  info: '#4ECDC4',

  // Gradients
  gradients: {
    primary: 'linear-gradient(135deg, #FF6B6B 0%, #FFA94D 100%)',
    primaryReverse: 'linear-gradient(135deg, #FFA94D 0%, #FF6B6B 100%)',
    dark: 'linear-gradient(135deg, #2C3E50 0%, #3d5a80 100%)',
    accent: 'linear-gradient(135deg, #4ECDC4 0%, #51CF66 100%)',
    subtle: 'linear-gradient(180deg, #FFFFFF 0%, #F8F9FA 100%)',
  },
} as const;

export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
} as const;

export const typography = {
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },

  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
  },

  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },

  lineHeight: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },
} as const;

export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  md: '0.5rem',     // 8px
  lg: '0.75rem',    // 12px
  xl: '1rem',       // 16px
  '2xl': '1.5rem',  // 24px
  full: '9999px',
} as const;

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
} as const;

export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  bounce: '500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
} as const;

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
} as const;

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  modalBackdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
} as const;

// Component-specific tokens
export const components = {
  button: {
    height: {
      sm: '2rem',      // 32px
      md: '2.75rem',   // 44px - Touch-friendly
      lg: '3.5rem',    // 56px
    },
    padding: {
      sm: `${spacing[2]} ${spacing[4]}`,
      md: `${spacing[3]} ${spacing[6]}`,
      lg: `${spacing[4]} ${spacing[8]}`,
    },
  },

  card: {
    padding: {
      sm: spacing[4],
      md: spacing[6],
      lg: spacing[8],
    },
    borderRadius: borderRadius['2xl'],
    shadow: shadows.lg,
  },

  input: {
    height: {
      sm: '2.5rem',   // 40px
      md: '3rem',     // 48px - Touch-friendly
      lg: '3.5rem',   // 56px
    },
    borderRadius: borderRadius.xl,
  },

  bottomNav: {
    height: '4.5rem',  // 72px - Touch-friendly
    iconSize: '1.5rem', // 24px
  },
} as const;

// Animation presets
export const animations = {
  fadeIn: {
    keyframes: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    duration: transitions.base,
  },

  slideUp: {
    keyframes: {
      from: { transform: 'translateY(10px)', opacity: 0 },
      to: { transform: 'translateY(0)', opacity: 1 },
    },
    duration: transitions.base,
  },

  scaleIn: {
    keyframes: {
      from: { transform: 'scale(0.95)', opacity: 0 },
      to: { transform: 'scale(1)', opacity: 1 },
    },
    duration: transitions.bounce,
  },

  shimmer: {
    keyframes: {
      '0%': { backgroundPosition: '-200% 0' },
      '100%': { backgroundPosition: '200% 0' },
    },
    duration: '1.5s',
    iterationCount: 'infinite',
  },
} as const;

// HCI Design Principles Applied:
// 1. Consistency: Centralized design tokens ensure visual consistency
// 2. Feedback: Transition tokens for smooth interactive feedback
// 3. Affordance: Touch-friendly sizes (44px+) for mobile interactions
// 4. Hierarchy: Typography scale for clear information hierarchy
// 5. Accessibility: High contrast colors, semantic color naming
// 6. Simplicity: Clean, organized token structure

/**
 * 테마 시스템
 * 컴포넌트별 일관된 스타일링을 위한 테마 정의
 */

import { tokens } from './tokens';

export const theme = {
  // 버튼 테마
  button: {
    base: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      border: 'none',
      borderRadius: tokens.borderRadius.md,
      fontWeight: tokens.typography.fontWeight.medium,
      cursor: 'pointer',
      transition: `all ${tokens.transition.normal}`,
      outline: 'none',
      '&:disabled': {
        opacity: 0.5,
        cursor: 'not-allowed',
      }
    },
    sizes: {
      sm: {
        padding: `${tokens.spacing[2]} ${tokens.spacing[3]}`,
        fontSize: tokens.typography.fontSize.sm,
      },
      md: {
        padding: `${tokens.spacing[3]} ${tokens.spacing[4]}`,
        fontSize: tokens.typography.fontSize.base,
      },
      lg: {
        padding: `${tokens.spacing[4]} ${tokens.spacing[6]}`,
        fontSize: tokens.typography.fontSize.lg,
      }
    },
    variants: {
      primary: {
        backgroundColor: tokens.colors.primary[500],
        color: tokens.colors.neutral[0],
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.primary[600],
        },
        '&:active': {
          backgroundColor: tokens.colors.primary[700],
        }
      },
      secondary: {
        backgroundColor: tokens.colors.secondary[500],
        color: tokens.colors.neutral[0],
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.secondary[600],
        }
      },
      success: {
        backgroundColor: tokens.colors.success[500],
        color: tokens.colors.neutral[0],
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.success[600],
        }
      },
      warning: {
        backgroundColor: tokens.colors.warning[500],
        color: tokens.colors.neutral[0],
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.warning[600],
        }
      },
      error: {
        backgroundColor: tokens.colors.error[500],
        color: tokens.colors.neutral[0],
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.error[600],
        }
      },
      ghost: {
        backgroundColor: 'transparent',
        color: tokens.colors.secondary[600],
        border: `1px solid ${tokens.colors.neutral[200]}`,
        '&:hover:not(:disabled)': {
          backgroundColor: tokens.colors.neutral[50],
        }
      }
    }
  },

  // 카드 테마
  card: {
    base: {
      backgroundColor: tokens.colors.neutral[0],
      border: `1px solid ${tokens.colors.neutral[200]}`,
      borderRadius: tokens.borderRadius.lg,
      boxShadow: tokens.boxShadow.base,
      overflow: 'hidden',
      transition: `box-shadow ${tokens.transition.normal}`,
    },
    interactive: {
      cursor: 'pointer',
      '&:hover': {
        boxShadow: tokens.boxShadow.md,
      }
    },
    padding: {
      sm: tokens.spacing[4],
      md: tokens.spacing[6],
      lg: tokens.spacing[8],
    }
  },

  // 입력 필드 테마
  input: {
    base: {
      width: '100%',
      padding: `${tokens.spacing[3]} ${tokens.spacing[4]}`,
      border: `1px solid ${tokens.colors.neutral[300]}`,
      borderRadius: tokens.borderRadius.md,
      fontSize: tokens.typography.fontSize.base,
      backgroundColor: tokens.colors.neutral[0],
      transition: `border-color ${tokens.transition.normal}`,
      outline: 'none',
      '&:focus': {
        borderColor: tokens.colors.primary[500],
        boxShadow: `0 0 0 3px ${tokens.colors.primary[100]}`,
      },
      '&:disabled': {
        backgroundColor: tokens.colors.neutral[100],
        color: tokens.colors.neutral[400],
        cursor: 'not-allowed',
      }
    },
    error: {
      borderColor: tokens.colors.error[500],
      '&:focus': {
        borderColor: tokens.colors.error[500],
        boxShadow: `0 0 0 3px ${tokens.colors.error[100]}`,
      }
    }
  },

  // 모달 테마
  modal: {
    overlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    content: {
      backgroundColor: tokens.colors.neutral[0],
      borderRadius: tokens.borderRadius.lg,
      boxShadow: tokens.boxShadow.lg,
      maxWidth: '500px',
      width: '90%',
      maxHeight: '90vh',
      overflow: 'auto',
    }
  },

  // 그리드 시스템
  grid: {
    container: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: `0 ${tokens.spacing[4]}`,
    },
    row: {
      display: 'flex',
      flexWrap: 'wrap',
      margin: `0 -${tokens.spacing[2]}`,
    },
    col: {
      padding: `0 ${tokens.spacing[2]}`,
    }
  },

  // 상태 표시
  status: {
    badge: {
      display: 'inline-flex',
      alignItems: 'center',
      padding: `${tokens.spacing[1]} ${tokens.spacing[3]}`,
      borderRadius: tokens.borderRadius.full,
      fontSize: tokens.typography.fontSize.sm,
      fontWeight: tokens.typography.fontWeight.medium,
    },
    pending: {
      backgroundColor: tokens.colors.warning[100],
      color: tokens.colors.warning[700],
    },
    approved: {
      backgroundColor: tokens.colors.success[100],
      color: tokens.colors.success[700],
    },
    rejected: {
      backgroundColor: tokens.colors.error[100],
      color: tokens.colors.error[700],
    },
    migrated: {
      backgroundColor: tokens.colors.primary[100],
      color: tokens.colors.primary[700],
    }
  }
};

export default theme;

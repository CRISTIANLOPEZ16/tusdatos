import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: { main: '#7041D9' },
    secondary: { main: '#285BD4' },
    background: { default: '#FFFFFF', paper: '#FFFFFF' },
    text: { primary: '#211B35', secondary: '#6D687B' },
  },
  shape: { borderRadius: 6 },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    button: { textTransform: 'none', fontWeight: 650 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { minHeight: 44, borderRadius: 11, paddingInline: 20 } },
    },
    MuiCssBaseline: {
      styleOverrides: {
        'button:focus-visible, a:focus-visible': {
          outline: '3px solid #285BD4', outlineOffset: 4,
        },
      },
    },
  },
});

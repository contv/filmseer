// Master theme override file
// Use this to quickly style any Material UI component which is a child of App globally
// Component names can be looked up under 'Global Class' on https://material-ui.com/api/
// e.g. ".MuiButton-root" is selected as Muibutton: { root: {...}} under overrides below
// These style overrides can be localised per component later if desired

import { createMuiTheme }  from '@material-ui/core/styles';

const theme = createMuiTheme({
  // Global styling
  palette: {
    primary: { 500: '#467fcf' },
  },
  typography: {
    subtitle1: {
      fontSize: "0.7rem",
    }
  },

  props: {
    // Set default props for a Mui component
    MuiCard: {
      variant: "outlined",
    }
  },

  overrides: {
    // Override a Mui component's styling
    MuiCard: {
      root: {
        maxWidth: 150,
      }
    },
    MuiCardMedia: {
      root: {
        height: 0,
        paddingTop: '148.15%',
      },
    },
    MuiCardHeader: {
      root: {
        display: 'flex',
        alignItems: 'center',
        padding: 8,
      },
      title: {
        fontSize: "0.9rem",
        overflow: "hidden",
        whiteSpace: "nowrap",
        textOverflow: "ellipsis",
        wordWrap: "break-word",
      },
      subheader: {
        fontSize: "0.7rem"
      }      
    },
    MuiCardContent: {
      root: {
        display: "flex",
        paddingTop: 0,
        paddingLeft: 8,
        '&:last-child': {
          paddingBottom: 8,
        },
      },
    }
  }
  
})

export default theme;
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import * as labs from 'vuetify/labs/components'
const vuetify = createVuetify({
  components: {
    ...components, 
    ...labs        
  },
  directives,

  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#FA8072',
          secondary: '#FFDAB9',
          accent: '#4682B4',
        },
      },
    },
  },
})

export default vuetify

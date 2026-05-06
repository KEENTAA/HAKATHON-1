import { provideHttpClient } from '@angular/common/http';
import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners,
  provideZonelessChangeDetection,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(),
    provideAnimationsAsync(),
 providePrimeNG({
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: '.dark-mode',
          cssLayer: {
            name: 'primeng',
            options: {
              prepend: true,
            },
          },
        },
      },
      translation: {
        startsWith: 'Empieza con',
        contains: 'Contiene',
        notContains: 'No contiene',
        endsWith: 'Termina con',
        equals: 'Igual a',
        notEquals: 'No igual a',
        noFilter: 'Sin filtro',
        lt: 'Menor que',
        lte: 'Menor o igual a',
        gt: 'Mayor que',
        gte: 'Mayor o igual a',
        is: 'Es',
        isNot: 'No es',
        before: 'Antes',
        after: 'Después',
        dateIs: 'Fecha es',
        dateIsNot: 'Fecha no es',
        dateBefore: 'Fecha antes de',
        dateAfter: 'Fecha después de',
        clear: 'Limpiar',
        apply: 'Aplicar',
        matchAll: 'Coincidir con todos',
        matchAny: 'Coincidir con cualquiera',
        addRule: 'Agregar regla',
        removeRule: 'Eliminar regla',
        accept: 'Aceptar',
        reject: 'Rechazar',
        choose: 'Elegir',
        upload: 'Subir',
        cancel: 'Cancelar',
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        dayNamesMin: ['D', 'L', 'M', 'X', 'J', 'V', 'S'],
        monthNames: [
          'Enero',
          'Febrero',
          'Marzo',
          'Abril',
          'Mayo',
          'Junio',
          'Julio',
          'Agosto',
          'Septiembre',
          'Octubre',
          'Noviembre',
          'Diciembre',
        ],
        monthNamesShort: [
          'Ene',
          'Feb',
          'Mar',
          'Abr',
          'May',
          'Jun',
          'Jul',
          'Ago',
          'Sep',
          'Oct',
          'Nov',
          'Dic',
        ],
        today: 'Hoy',
        weekHeader: 'Sem',
        firstDayOfWeek: 1,
        dateFormat: 'dd/mm/yy',
        weak: 'Débil',
        medium: 'Medio',
        strong: 'Fuerte',
        passwordPrompt: 'Escriba una contraseña',
        emptyFilterMessage: 'No se encontraron resultados',
        emptyMessage: 'No hay opciones disponibles',
      },
    }),
  ],
};

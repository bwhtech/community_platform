import { useMediaQuery } from '@vueuse/core'

// Matches Tailwind's `sm` breakpoint: below it the app uses the mobile shell.
export function useIsMobile() {
  return useMediaQuery('(max-width: 639px)')
}

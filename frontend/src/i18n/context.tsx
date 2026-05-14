import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { Lang, T } from './types'
import { dict } from './dict'

interface I18nContextValue {
  lang: Lang
  t: T
  setLang: (lang: Lang) => void
}

const I18nContext = createContext<I18nContextValue | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const saved = localStorage.getItem('arbiter-lang')
    return saved === 'en' ? 'en' : 'zh'
  })

  const setLang = useCallback((next: Lang) => {
    localStorage.setItem('arbiter-lang', next)
    setLangState(next)
  }, [])

  const t = dict[lang]

  return (
    <I18nContext.Provider value={{ lang, t, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}

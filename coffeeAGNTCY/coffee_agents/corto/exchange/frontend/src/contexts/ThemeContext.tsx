/**
 * Copyright AGNTCY Contributors (https://github.com/agntcy)
 * SPDX-License-Identifier: Apache-2.0
 **/

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react"

type Theme = "light" | "dark"

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
  isLightMode: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem("theme")
    return (savedTheme as Theme) || "dark"
  })

  useEffect(() => {
    // Add the theme-switching class to prevent transition flashes
    document.body.classList.add("theme-switching")

    if (theme === "light") {
      document.body.setAttribute("data-theme", "light")
    } else {
      document.body.removeAttribute("data-theme")
    }

    localStorage.setItem("theme", theme)

    // Remove the theme-switching class after a short delay
    const timeoutId = setTimeout(() => {
      document.body.classList.remove("theme-switching")
    }, 100)

    return () => {
      clearTimeout(timeoutId)
    }
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  const toggleTheme = () => {
    setThemeState((prevTheme) => (prevTheme === "light" ? "dark" : "light"))
  }

  const isLightMode = theme === "light"

  const value: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    isLightMode,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}

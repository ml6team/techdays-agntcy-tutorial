/**
 * Copyright AGNTCY Contributors (https://github.com/agntcy)
 * SPDX-License-Identifier: Apache-2.0
 **/

import { useTheme } from "@/contexts/ThemeContext"

interface ThemeImageMap {
  light: string
  dark: string
}

export const useThemeImage = (imageMap: ThemeImageMap): string => {
  const { theme } = useTheme()

  return theme === "light" ? imageMap.light : imageMap.dark
}

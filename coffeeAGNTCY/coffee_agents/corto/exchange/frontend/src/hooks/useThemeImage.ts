/**
 * Copyright AGNTCY Contributors (https://github.com/agntcy)
 * SPDX-License-Identifier: Apache-2.0
 **/

import { useEffect, useState } from "react"

interface ThemeImageMap {
  light: string
  dark: string
}

export const useThemeImage = (imageMap: ThemeImageMap): string => {
  const [currentImage, setCurrentImage] = useState<string>(imageMap.dark)

  useEffect(() => {
    const updateImage = async () => {
      const theme = document.body.getAttribute("data-theme")

      if (theme === "light") {
        try {
          const response = await fetch(imageMap.light)
          if (response.ok) {
            setCurrentImage(imageMap.light)
          } else {
            setCurrentImage(imageMap.dark)
          }
        } catch {
          setCurrentImage(imageMap.dark)
        }
      } else {
        setCurrentImage(imageMap.dark)
      }
    }

    updateImage()

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (
          mutation.type === "attributes" &&
          mutation.attributeName === "data-theme"
        ) {
          updateImage()
        }
      })
    })

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-theme"],
    })

    return () => observer.disconnect()
  }, [imageMap])

  return currentImage
}

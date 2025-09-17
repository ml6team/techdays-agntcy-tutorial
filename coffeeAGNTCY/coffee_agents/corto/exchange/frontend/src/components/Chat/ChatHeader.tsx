/**
 * Copyright AGNTCY Contributors (https://github.com/agntcy)
 * SPDX-License-Identifier: Apache-2.0
 **/

import React from "react"
import { Trash2 } from "lucide-react"
import collapseIcon from "@/assets/collapse.png"

interface ChatHeaderProps {
  onMinimize?: () => void
  onClearConversation?: () => void
  isMinimized?: boolean
  showActions?: boolean
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  onMinimize,
  onClearConversation,
  isMinimized,
  showActions = false,
}) => {
  if (!showActions) {
    return null
  }

  return (
    <div className="border-control-border-weak flex w-full items-center justify-between border-b px-4 py-2 pr-2 sm:px-6 sm:pr-4 md:px-8 md:pr-8 lg:pl-8 lg:pr-4">
      <span className="chat-header-text">Chat</span>

      <div className="flex h-7 w-16 gap-2">
        {onMinimize && (
          <div className="flex h-7 w-7 items-center justify-center rounded-lg p-1">
            <button
              onClick={onMinimize}
              className="flex h-5 w-5 items-center justify-center rounded transition-colors"
              title={isMinimized ? "Maximize" : "Minimize"}
            >
              <img
                src={collapseIcon}
                alt={isMinimized ? "Maximize" : "Minimize"}
                className={`chat-header-icon h-5 w-5 ${isMinimized ? "rotate-180" : ""}`}
              />
            </button>
          </div>
        )}
        {onClearConversation && (
          <div className="flex h-7 w-7 items-center justify-center rounded-lg p-1">
            <button
              onClick={onClearConversation}
              className="flex h-5 w-5 items-center justify-center rounded transition-colors"
              title="Clear conversation"
            >
              <Trash2 className="chat-header-trash-icon h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatHeader

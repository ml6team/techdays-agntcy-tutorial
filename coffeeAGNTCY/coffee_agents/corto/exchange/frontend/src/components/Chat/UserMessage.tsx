/**
 * Copyright AGNTCY Contributors (https://github.com/agntcy)
 * SPDX-License-Identifier: Apache-2.0
 **/

import React from "react"
import { User, Trash2 } from "lucide-react"

interface UserMessageProps {
  content: string
  onMinimize?: () => void
  onClearConversation?: () => void
  isMinimized?: boolean
  showActions?: boolean
}

const UserMessage: React.FC<UserMessageProps> = ({
  content,
  onMinimize,
  onClearConversation,
  isMinimized,
  showActions = false,
}) => {
  return (
    <div className="flex min-h-[2.5rem] w-full flex-row items-start gap-1">
      <div className="chat-avatar-container flex h-10 w-10 flex-none items-center justify-center rounded-full bg-action-background">
        <User size={22} className="text-white" />
      </div>

      <div
        className="flex min-h-[2.5rem] flex-1 flex-col items-start justify-center rounded p-1 px-2"
        style={{ maxWidth: "calc(100% - 3rem)" }}
      >
        <div
          className={`flex w-full items-center rounded p-1 px-2 ${showActions ? "justify-between" : ""}`}
        >
          <div className="break-words font-inter text-sm font-normal leading-5 text-chat-text">
            {content}
          </div>

          {showActions && (
            <div className="ml-3 flex flex-shrink-0 gap-2">
              {onMinimize && (
                <button
                  onClick={onMinimize}
                  className="chat-avatar-container flex h-6 w-6 items-center justify-center rounded-full bg-action-background shadow-sm transition-colors hover:bg-action-background-hover"
                  title={isMinimized ? "Maximize" : "Minimize"}
                >
                  {isMinimized ? (
                    <svg
                      className="h-3 w-3 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 8V6a2 2 0 012-2h2M4 16v2a2 2 0 002 2h2m8-16h2a2 2 0 012 2v2m-4 12h2a2 2 0 002-2v-2"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="h-3 w-3 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 12H4"
                      />
                    </svg>
                  )}
                </button>
              )}
              {onClearConversation && (
                <button
                  onClick={onClearConversation}
                  className="chat-avatar-container flex h-6 w-6 items-center justify-center rounded-full bg-action-background shadow-sm transition-colors hover:bg-action-background-hover"
                  title="Clear conversation"
                >
                  <Trash2 className="h-3 w-3 text-white" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserMessage

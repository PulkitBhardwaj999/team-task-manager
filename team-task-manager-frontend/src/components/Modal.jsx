import { useState } from 'react';

export function Modal({ isOpen, title, onClose, children, actions }) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 animate-fade-in"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-slide-up">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {title}
            </h2>
          </div>

          {/* Body */}
          <div className="px-6 py-4">
            {children}
          </div>

          {/* Footer */}
          {actions && (
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-800 flex gap-3 justify-end">
              {actions.map((action) => (
                <button
                  key={action.label}
                  onClick={action.onClick}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    action.variant === 'danger'
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : action.variant === 'primary'
                      ? 'bg-primary-500 hover:bg-primary-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { useModeStore } from '@/stores/modeStore';
import { WALKTHROUGH_STORAGE_KEY } from '@/components/walkthrough';

export default function Header() {
  const { isAdvancedMode, toggleMode } = useModeStore();
  const [showHelpMenu, setShowHelpMenu] = useState(false);

  const handleRestartTour = () => {
    localStorage.removeItem(WALKTHROUGH_STORAGE_KEY);
    window.location.reload();
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowHelpMenu(false);
    if (showHelpMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showHelpMenu]);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex-1" />
        
        <div className="flex items-center gap-4">
          {/* Help Menu */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowHelpMenu(!showHelpMenu);
              }}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition"
            >
              <span>❓</span>
              <span>Help</span>
            </button>
            
            {showHelpMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <button
                  onClick={handleRestartTour}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <span>🎯</span>
                  Restart Tour
                </button>
                <a
                  href="mailto:support@aivaro.com"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <span>📧</span>
                  Contact Support
                </a>
              </div>
            )}
          </div>

          {/* Mode Toggle */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {isAdvancedMode ? 'Advanced Mode' : 'Simple Mode'}
            </span>
            <button
              onClick={toggleMode}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isAdvancedMode ? 'bg-primary-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isAdvancedMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

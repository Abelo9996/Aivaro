'use client';

import { useState, useEffect } from 'react';
import { HelpCircle, RotateCcw, Mail } from 'lucide-react';
import { WALKTHROUGH_STORAGE_KEY } from '@/components/walkthrough';

export default function Header() {
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
      <div className="flex items-center justify-end">
        {/* Help Menu */}
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowHelpMenu(!showHelpMenu);
            }}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition px-3 py-2 rounded-lg hover:bg-gray-50"
          >
            <HelpCircle className="w-4 h-4" />
            <span>Help</span>
          </button>
          
          {showHelpMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <button
                onClick={handleRestartTour}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Restart Tour
              </button>
              <a
                href="mailto:support@aivaro.com"
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <Mail className="w-4 h-4" />
                Contact Support
              </a>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

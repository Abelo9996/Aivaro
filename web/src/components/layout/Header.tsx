'use client';

import { useModeStore } from '@/stores/modeStore';

export default function Header() {
  const { isAdvancedMode, toggleMode } = useModeStore();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex-1" />
        
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
    </header>
  );
}

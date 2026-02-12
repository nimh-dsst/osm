import React from 'react';
import { Settings } from 'lucide-react';

export function LoadingSpinner() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Settings className="w-8 h-8 animate-spin text-blue-600" />
    </div>
  );
}
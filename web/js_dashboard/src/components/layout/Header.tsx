import React from 'react';
import { BarChart } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-6 flex items-center gap-3">
        <BarChart className="w-8 h-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">OpenSciMetrics Dashboard</h1>
      </div>
    </header>
  );
}
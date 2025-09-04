import React from 'react';
import { Calendar } from 'lucide-react';

interface Props {
  fromYear: number;
  toYear: number;
  onFromYearChange: (year: number) => void;
  onToYearChange: (year: number) => void;
}

export function TimeRangeFilter({ fromYear, toYear, onFromYearChange, onToYearChange }: Props) {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: currentYear - 1999 }, (_, i) => 2000 + i);

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Calendar className="w-5 h-5 text-blue-600" />
        <h3 className="text-sm font-medium text-gray-700">Time Range</h3>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="fromYear" className="block text-sm text-gray-600 mb-1">
            From
          </label>
          <select
            id="fromYear"
            value={fromYear}
            onChange={(e) => onFromYearChange(Number(e.target.value))}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="toYear" className="block text-sm text-gray-600 mb-1">
            To
          </label>
          <select
            id="toYear"
            value={toYear}
            onChange={(e) => onToYearChange(Number(e.target.value))}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
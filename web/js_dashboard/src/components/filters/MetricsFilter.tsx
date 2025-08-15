import React from 'react';
import { Filter } from 'lucide-react';

interface Props {
  selectedMetric: string;
  onMetricChange: (metric: string) => void;
}

export function MetricsFilter({ selectedMetric, onMetricChange }: Props) {
  const metrics = [
    { value: 'openCode', label: 'Open Code' },
    { value: 'openData', label: 'Open Data' },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Filter className="w-5 h-5 text-blue-600" />
        <h3 className="text-sm font-medium text-gray-700">Metrics</h3>
      </div>
      <select
        value={selectedMetric}
        onChange={(e) => onMetricChange(e.target.value)}
        className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
      >
        {metrics.map((metric) => (
          <option key={metric.value} value={metric.value}>
            {metric.label}
          </option>
        ))}
      </select>
    </div>
  );
}
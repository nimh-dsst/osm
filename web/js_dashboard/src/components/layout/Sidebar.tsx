import React from 'react';
import { TimeRangeFilter } from '../filters/TimeRangeFilter';
import { MetricsFilter } from '../filters/MetricsFilter';

interface Props {
  fromYear: number;
  toYear: number;
  selectedMetric: string;
  onFromYearChange: (year: number) => void;
  onToYearChange: (year: number) => void;
  onMetricChange: (metric: string) => void;
}

export function Sidebar({
  fromYear,
  toYear,
  selectedMetric,
  onFromYearChange,
  onToYearChange,
  onMetricChange,
}: Props) {
  return (
    <div className="w-64 bg-gray-50 p-4 border-r border-gray-200">
      <TimeRangeFilter
        fromYear={fromYear}
        toYear={toYear}
        onFromYearChange={onFromYearChange}
        onToYearChange={onToYearChange}
      />
      <MetricsFilter selectedMetric={selectedMetric} onMetricChange={onMetricChange} />
    </div>
  );
}
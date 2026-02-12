import React from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface Props {
  children: React.ReactNode;
  fromYear: number;
  toYear: number;
  selectedMetric: string;
  onFromYearChange: (year: number) => void;
  onToYearChange: (year: number) => void;
  onMetricChange: (metric: string) => void;
}

export function Layout({
  children,
  fromYear,
  toYear,
  selectedMetric,
  onFromYearChange,
  onToYearChange,
  onMetricChange,
}: Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar
          fromYear={fromYear}
          toYear={toYear}
          selectedMetric={selectedMetric}
          onFromYearChange={onFromYearChange}
          onToYearChange={onToYearChange}
          onMetricChange={onMetricChange}
        />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
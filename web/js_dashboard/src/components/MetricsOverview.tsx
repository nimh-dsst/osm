import React from 'react';
import { BarChart3, Book, Globe, Code, Database } from 'lucide-react';
import type { MetricsSummary } from '../types/metrics';

interface Props {
  summary: MetricsSummary;
}

export function MetricsOverview({ summary }: Props) {
  const cards = [
    {
      title: 'Total Records',
      value: summary.totalRecords.toLocaleString(),
      icon: BarChart3,
      color: 'text-blue-600',
    },
    {
      title: 'Open Code %',
      value: `${summary.openCodePercentage.toFixed(1)}%`,
      icon: Code,
      color: 'text-green-600',
    },
    {
      title: 'Open Data %',
      value: `${summary.openDataPercentage.toFixed(1)}%`,
      icon: Database,
      color: 'text-purple-600',
    },
    {
      title: 'Unique Journals',
      value: summary.uniqueJournals.toLocaleString(),
      icon: Book,
      color: 'text-orange-600',
    },
    {
      title: 'Countries',
      value: summary.uniqueCountries.toLocaleString(),
      icon: Globe,
      color: 'text-teal-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
      {cards.map((card) => (
        <div key={card.title} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 text-sm font-medium">{card.title}</h3>
            <card.icon className={`w-5 h-5 ${card.color}`} />
          </div>
          <p className="text-2xl font-semibold">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
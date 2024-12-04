import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface DataPoint {
  year: number;
  openCode: number;
  openData: number;
}

interface Props {
  data: DataPoint[];
  selectedMetric: string;
}

export function TimeSeriesChart({ data, selectedMetric }: Props) {
  const metricColors = {
    openCode: '#10B981',
    openData: '#8B5CF6',
  };

  const metricLabels = {
    openCode: 'Open Code %',
    openData: 'Open Data %',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-8">
      <h2 className="text-lg font-semibold mb-4">Open Science Trends Over Time</h2>
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey={selectedMetric}
              stroke={metricColors[selectedMetric as keyof typeof metricColors]}
              name={metricLabels[selectedMetric as keyof typeof metricLabels]}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { LoadingSpinner } from './components/layout/LoadingSpinner';
import { MetricsOverview } from './components/metrics/MetricsOverview';
import { TimeSeriesChart } from './components/charts/TimeSeriesChart';
import { DistributionChart } from './components/distributions/DistributionChart';
import { useMetrics } from './hooks/useMetrics';

function App() {
  const [fromYear, setFromYear] = useState(2000);
  const [toYear, setToYear] = useState(2024);
  const [selectedMetric, setSelectedMetric] = useState('openCode');
  
  const { loading, error, summary, timeSeriesData, countryData, journalData } = useMetrics();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-600">Error: {error.message}</p>
      </div>
    );
  }

  const filteredTimeSeriesData = timeSeriesData.filter(
    (data) => data.year >= fromYear && data.year <= toYear
  );

  return (
    <Layout
      fromYear={fromYear}
      toYear={toYear}
      selectedMetric={selectedMetric}
      onFromYearChange={setFromYear}
      onToYearChange={setToYear}
      onMetricChange={setSelectedMetric}
    >
      <MetricsOverview summary={summary} />
      <TimeSeriesChart 
        data={filteredTimeSeriesData}
        selectedMetric={selectedMetric}
      />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <DistributionChart
          title="Top 10 Countries by Publications"
          data={countryData}
          color="#3B82F6"
        />
        <DistributionChart
          title="Top 10 Journals by Publications"
          data={journalData}
          color="#10B981"
        />
      </div>
    </Layout>
  );
}

export default App;
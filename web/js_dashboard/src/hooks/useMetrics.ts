import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { MetricsSummary } from '../types/metrics';

export function useMetrics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [summary, setSummary] = useState<MetricsSummary>({
    totalRecords: 0,
    openCodePercentage: 0,
    openDataPercentage: 0,
    uniqueJournals: 0,
    uniqueCountries: 0,
  });
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [countryData, setCountryData] = useState([]);
  const [journalData, setJournalData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryData, timeSeriesData, countryData, journalData] = await Promise.all([
          api.getSummary(),
          api.getTimeSeries(),
          api.getCountryDistribution(),
          api.getJournalDistribution(),
        ]);

        setSummary(summaryData);
        setTimeSeriesData(timeSeriesData);
        setCountryData(countryData);
        setJournalData(journalData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch metrics'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { loading, error, summary, timeSeriesData, countryData, journalData };
}
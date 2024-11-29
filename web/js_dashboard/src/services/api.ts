import axios from 'axios';
import type { MetricsSummary } from '../types/metrics';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  async getSummary(): Promise<MetricsSummary> {
    const { data } = await axios.get(`${API_BASE_URL}/summary`);
    return data;
  },

  async getTimeSeries() {
    const { data } = await axios.get(`${API_BASE_URL}/timeseries`);
    return data;
  },

  async getCountryDistribution() {
    const { data } = await axios.get(`${API_BASE_URL}/country-distribution`);
    return Object.entries(data).map(([name, value]) => ({ name, value }));
  },

  async getJournalDistribution() {
    const { data } = await axios.get(`${API_BASE_URL}/journal-distribution`);
    return Object.entries(data).map(([name, value]) => ({ name, value }));
  }
};
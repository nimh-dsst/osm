export interface MetricsData {
  is_open_code: boolean;
  is_open_data: boolean;
  year: number;
  pmid: number;
  journal: string;
  affiliation_country: string;
  funder: string;
  data_tags: string[];
  created_at: string;
}

export interface MetricsSummary {
  totalRecords: number;
  openCodePercentage: number;
  openDataPercentage: number;
  uniqueJournals: number;
  uniqueCountries: number;
}
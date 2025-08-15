export const formatters = {
  number: (value: number): string => {
    return value.toLocaleString();
  },

  percentage: (value: number): string => {
    return `${value.toFixed(1)}%`;
  },

  date: (value: string): string => {
    return new Date(value).toLocaleDateString();
  }
};
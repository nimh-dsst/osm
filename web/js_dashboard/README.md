# OpenSciMetrics Javascript Dashboard

## Features

- 📊 Interactive data visualization of open science trends
- 📈 Time series analysis of open code and data practices
- 🔍 Advanced filtering capabilities
- 📱 Responsive design for all devices
- ⚡ Real-time data processing
- 🎯 Performance-optimized for large datasets

## Tech Stack

### Frontend
- React with TypeScript
- Recharts for data visualization
- Tailwind CSS for styling
- Axios for API communication
- Lucide React for icons

### Backend
- FastAPI (Python)
- Pandas for data processing
- Uvicorn ASGI server
- Parquet file handling

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Virtual environment (recommended)

### Data Setup

1. Place your `matches.parquet` file in the `backend` directory:
```
backend/
  ├── matches.parquet  # Place your Parquet file here
  ├── main.py
  ├── routers/
  └── services/
```

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
```

2. Install dependencies:
```bash
pip install fastapi uvicorn pandas pyarrow
```

3. Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   └── metrics.py         # API route definitions
│   └── services/
│       └── data_service.py    # Data processing logic
│
├── src/
│   ├── components/            # React components
│   │   ├── charts/           # Data visualization components
│   │   ├── filters/          # Filter components
│   │   ├── layout/           # Layout components
│   │   └── metrics/          # Metric display components
│   ├── hooks/                # Custom React hooks
│   ├── services/             # API services
│   ├── types/                # TypeScript type definitions
│   └── utils/                # Utility functions
│
└── public/                   # Static assets
```

## API Endpoints

- `GET /api/summary` - Get overall metrics summary
- `GET /api/timeseries` - Get time series data
- `GET /api/country-distribution` - Get data distribution by country
- `GET /api/journal-distribution` - Get data distribution by journal

## Development

### Code Style

- Frontend follows TypeScript best practices
- Backend uses Python type hints
- ESLint and Prettier for code formatting
- Pre-commit hooks for code quality

## Acknowledgments

- Data source: [OpenSciMetrics Dataset](https://github.com/nimh-dsst/osm)
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- Visualization powered by [Recharts](https://recharts.org/)
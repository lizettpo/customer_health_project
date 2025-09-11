# Customer Health Dashboard Frontend

A React TypeScript application for monitoring customer health scores and engagement metrics.

## Features

- **Dashboard Overview**: Real-time statistics and customer health distribution
- **Customer Management**: Browse and filter customers by health status
- **Health Score Details**: Detailed breakdown of health factors for individual customers
- **Historical Tracking**: View historical health scores and trends
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **React 18** with TypeScript
- **React Router** for navigation
- **Axios** for API calls
- **Tailwind CSS** for styling
- **Custom Hooks** for state management

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Tailwind CSS:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`.

## Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard/       # Dashboard-related components
│   └── HealthScore/     # Health score detail components
├── services/            # API service layer
│   ├── api.ts          # Base API configuration
│   ├── customerService.ts    # Customer-related API calls
│   └── healthScoreService.ts # Health score API calls
├── hooks/               # Custom React hooks
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── App.tsx             # Main application component
```

## API Integration

The frontend communicates with the FastAPI backend through a well-structured service layer:

### Service Layer (`src/services/`)

- **`api.ts`**: Base Axios configuration with interceptors
- **`customerService.ts`**: Customer-related API endpoints
- **`healthScoreService.ts`**: Health score calculation and retrieval

### Custom Hooks (`src/hooks/`)

- **`useCustomers`**: Fetch and manage customer data
- **`useDashboardStats`**: Dashboard statistics
- **`useHealthScore`**: Individual customer health scores

## Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Available Scripts

- `npm start`: Start development server
- `npm test`: Run tests
- `npm run build`: Build for production
- `npm run eject`: Eject from Create React App (not recommended)

## Key Components

### Dashboard
- **DashboardStats**: Overview metrics and health distribution
- **CustomersList**: Paginated customer list with filtering
- **Dashboard**: Main dashboard container

### Health Score Detail
- **CustomerHealthDetail**: Complete health score breakdown
- **HealthFactorCard**: Individual health factor display
- **HistoricalChart**: Historical score visualization

## Styling

The application uses Tailwind CSS for consistent and responsive styling. Custom health score colors are defined in the utility functions to provide visual feedback based on score ranges:

- **Healthy (75-100)**: Green
- **At Risk (60-74)**: Yellow/Orange  
- **Critical (0-59)**: Red

## Error Handling

- API errors are handled gracefully with user-friendly messages
- Loading states provide visual feedback during API calls
- Retry functionality for failed requests

## Performance Considerations

- API calls are optimized with proper error handling and loading states
- Components use React hooks for efficient state management
- Tailwind CSS provides optimized styling with minimal bundle size
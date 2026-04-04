import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ROUTER_V7_FUTURE_FLAGS } from './routerFuture';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { assertProductionAuthBypassNotEnabled } from './auth/authEnvGuard';
import { AuthProvider } from './hooks/useAuth';
import App from './App';
import './index.css';

assertProductionAuthBypassNotEnabled();

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter future={ROUTER_V7_FUTURE_FLAGS}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);

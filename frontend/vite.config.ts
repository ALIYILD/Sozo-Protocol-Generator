import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { isUnsafeProductionAuthBypass } from './src/auth/authBypassPolicy';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  if (isUnsafeProductionAuthBypass(command === 'build', env.VITE_AUTH_BYPASS)) {
    throw new Error(
      'VITE_AUTH_BYPASS cannot be enabled for production builds. ' +
        'Unset it in .env.production, CI, and release pipelines.',
    );
  }

  return {
    plugins: [react()],
    base: '/',
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  };
});

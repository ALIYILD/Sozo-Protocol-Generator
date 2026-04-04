/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Set to "true" to skip SPA login (development only). */
  readonly VITE_AUTH_BYPASS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

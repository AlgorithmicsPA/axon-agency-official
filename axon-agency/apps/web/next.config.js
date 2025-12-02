import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    };
    return config;
  },
  // NOTA: Los rewrites están deshabilitados porque el frontend usa API_BASE_URL directamente
  // Si se necesita proxy, descomentar y ajustar el puerto (8090, no 8080)
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: 'http://localhost:8090/api/:path*',
  //     },
  //   ];
  // },
};

export default nextConfig;

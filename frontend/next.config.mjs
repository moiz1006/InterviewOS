/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Fail the production build on type errors / lint errors rather than
  // silently shipping them — the opposite of Next's permissive defaults.
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // API paths are proxied by middleware so the request's trailing slash is preserved.
  skipTrailingSlashRedirect: true,
};

export default nextConfig;

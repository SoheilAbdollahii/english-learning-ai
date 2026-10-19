import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Django API routes use trailing slashes; preserve the incoming API path
  // so Next.js does not redirect /api/.../ to /api/....
  skipTrailingSlashRedirect: true,
};

export default nextConfig;

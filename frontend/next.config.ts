import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Django API routes require trailing slashes. Make slash-terminated paths
  // canonical so Next.js does not redirect /api/.../ to /api/.... This also
  // establishes a trailing-slash URL convention for frontend pages.
  trailingSlash: true,
  // Keep middleware in control of any path-specific slash handling.
  skipTrailingSlashRedirect: true,
};

export default nextConfig;

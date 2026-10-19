import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Django API endpoints use trailing slashes. Keep Next.js from stripping them
  // before middleware can proxy the request.
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
};

export default nextConfig;

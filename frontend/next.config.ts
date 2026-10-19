import type { NextConfig } from "next";

const backendApiUrl = (process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Django API routes require trailing slashes, so slash-terminated URLs are canonical.
  trailingSlash: true,
  async rewrites() {
    return [
      {
        // Keep the trailing slash on both sides; Django's URLconf depends on it.
        source: "/api/:path*/",
        destination: `${backendApiUrl}/api/:path*/`,
      },
    ];
  },
};

export default nextConfig;

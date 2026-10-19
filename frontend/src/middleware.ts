import { NextRequest, NextResponse } from "next/server";

const backendApiUrl = (process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export function middleware(request: NextRequest) {
  const destination = new URL(
    `${request.nextUrl.pathname}${request.nextUrl.search}`,
    backendApiUrl,
  );

  return NextResponse.rewrite(destination);
}

export const config = {
  matcher: ["/api/:path*"],
};

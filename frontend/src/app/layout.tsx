import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "English Learning AI",
  description: "An AI-powered English learning workspace"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr">
      <body>{children}</body>
    </html>
  );
}

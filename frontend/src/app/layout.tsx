import type { Metadata } from "next";
import "./globals.css";
import { LocaleProvider, LocaleSwitcher } from "./components/locale-provider";

export const metadata: Metadata = {
  title: "Wordwise — English Learning Studio",
  description:
    "A calm, structured space for English writing, reading, vocabulary practice, and steady learning progress.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr">
      <body><LocaleProvider><LocaleSwitcher />{children}</LocaleProvider></body>
    </html>
  );
}

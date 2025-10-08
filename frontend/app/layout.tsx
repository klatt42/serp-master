import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "SERP-Master | Modern SEO Analysis for Small Business",
  description: "Know where you stand. Find where to compete. Complete SEO, AEO, and entity clarity analysis powered by AI.",
  keywords: ["SEO", "AEO", "Answer Engine Optimization", "Entity Clarity", "Small Business SEO"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-gray-50 text-gray-900" suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}

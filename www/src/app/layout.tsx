import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorldCup Guide | 축구 월드컵 안내",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

import type { NextConfig } from "next";

const API_PORT = process.env.API_PORT || process.env.VITE_API_PORT || "8000";
// 로컬/도커: 프론트·백엔드가 같은 호스트라 127.0.0.1로 충분.
// Vercel: 서버리스 환경엔 127.0.0.1에 백엔드가 없어 항상 404였음 — 백엔드 공개 주소를 지정해야 함.
const API_ORIGIN = (process.env.BACKEND_ORIGIN?.trim() || `http://127.0.0.1:${API_PORT}`).replace(
  /\/$/,
  "",
);

const nextConfig: NextConfig = {
  devIndicators: false,
  async rewrites() {
    return [
      { source: "/chat", destination: `${API_ORIGIN}/chat` },
      { source: "/weather", destination: `${API_ORIGIN}/weather` },
      { source: "/signup", destination: `${API_ORIGIN}/signup` },
      { source: "/ping", destination: `${API_ORIGIN}/ping` },
      { source: "/db-check", destination: `${API_ORIGIN}/db-check` },
      { source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` },
      {
        source: "/google-gemini/:path*",
        destination: "https://generativelanguage.googleapis.com/:path*",
      },
    ];
  },
};

export default nextConfig;

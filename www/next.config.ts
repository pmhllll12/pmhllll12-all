import type { NextConfig } from "next";

const API_PORT = process.env.API_PORT || process.env.VITE_API_PORT || "8000";
const API_ORIGIN = `http://127.0.0.1:${API_PORT}`;

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

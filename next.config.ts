import type { NextConfig } from "next"

// El sitio sigue siendo HTML estático (public/), generado por tools/generate_dashboard.py.
// Next.js solo agrega el login y protege todo con proxy.ts.
const sinCache = [{ key: "Cache-Control", value: "no-cache, no-store, must-revalidate" }]

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/", destination: "/index.html" },
      { source: "/meetings/:id", destination: "/meetings/:id/index.html" },
    ]
  },
  async headers() {
    return ["/", "/index.html", "/meetings.json", "/config.json", "/meetings/:path*", "/docs/:path*"].map(
      (source) => ({ source, headers: sinCache }),
    )
  },
}

export default nextConfig

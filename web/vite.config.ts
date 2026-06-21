// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - tanstackStart, viteReact, tailwindcss, tsConfigPaths, nitro (build-only using cloudflare as a default target),
//     componentTagger (dev-only), VITE_* env injection, @ path alias, React/TanStack dedupe,
//     error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
    // Static deploy (Render Static Site): client-render every route against the
    // pre-built public/data/*.json. No SSR server at runtime, so SSR buys nothing.
    // Outside a Lovable sandbox the wrapper skips Nitro entirely → plain static Vite build.
    spa: { enabled: true },
  },
  // The wrapper forces the server host to IPv6 "::". The SPA-shell prerender step
  // starts a Vite preview server that inherits that host and fails on IPv4-only
  // build hosts with EAFNOSUPPORT. Pin the preview server to IPv4 loopback.
  vite: {
    preview: { host: "127.0.0.1" },
  },
});

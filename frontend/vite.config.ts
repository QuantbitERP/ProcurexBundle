// Static React build served by the procurex Frappe app at /procurex.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";
import type { ConfigEnv } from "vite";

const BASE = process.env.PROCUREX_ASSET_BASE ?? "/assets/procurex/ui/";
const BASEPATH = process.env.PROCUREX_BASEPATH ?? "/procurex";

const routerBasepath = {
  name: "procurex:router-basepath",
  enforce: "pre" as const,
  transform(code: string, id: string) {
    const path = id.replace(/\\/g, "/");
    if (path.endsWith("/src/components/procurex/SupplierStagingScreen.tsx")) {
      return code.replace(
        'window.location.href = "/auth"',
        `window.location.href = ${JSON.stringify(`${BASEPATH}/auth`)}`,
      );
    }
    if (!path.endsWith("/src/router.tsx")) return null;
    if (!code.includes("createRouter({")) return null;
    return code.replace("createRouter({", `createRouter({ basepath: ${JSON.stringify(BASEPATH)},`);
  },
};

const bundleConfig = defineConfig({
  plugins: [routerBasepath],
  tanstackStart: {
    router: { basepath: BASEPATH },
    server: { entry: "server" },
    spa: { enabled: true },
  },
  nitro: false,
  vite: {
    base: BASE,
  },
});

export default async (env: ConfigEnv) => {
  const config = await bundleConfig(env);
  // TanStack prerenders through Vite preview, which uses base for request routing.
  // Keep the compiled asset URLs separate from the Frappe page route.
  if (env.isPreview) config.base = `${BASEPATH}/`;
  return config;
};

import { createOpenCode2TuiPlugin } from "/home/notforsaleyo/.local/lib/node_modules/opencode-codex-usage/dist/opencode2-tui.js";
import { createQuotaMonitor } from "/home/notforsaleyo/.local/lib/node_modules/opencode-codex-usage/dist/lib/codex-usage-monitor.js";
import { createQuotaFooter } from "./footer.tsx";

// Node's maximum supported interval: 24 days, 20 hours, 31 minutes, 23.647 seconds.
// Keep this customization separate from the installed upstream package.
const MAX_POLL_MS = 2_147_483_647;
export default {
  id: "opencode-codex-usage",
  setup(context) {
    const footer = createQuotaFooter(context);
    const upstream = createOpenCode2TuiPlugin(undefined, (options) =>
      createQuotaMonitor({
        ...options,
        pollMs: MAX_POLL_MS,
        threshold: "never",
        notify: () => {},
        async probe() {
          footer.loading();
          try {
            const snapshot = await options.probe();
            footer.update(snapshot);
            return snapshot;
          } catch (error) {
            footer.fail();
            throw error;
          }
        },
      }),
    );
    let cleanup;
    try {
      cleanup = upstream.setup({
      ...context,
      keymap: {
        ...context.keymap,
        layer(build) {
          return context.keymap.layer(() => {
            const layer = build();
            return {
              ...layer,
              // Register /codex-usage without claiming any keyboard shortcut.
              commands: layer.commands.map(({ bind, ...command }) => command),
              bindings: [],
            };
          });
        },
      },
      });
    } catch (error) {
      footer.dispose();
      throw error;
    }
    return () => {
      try {
        cleanup?.();
      } finally {
        footer.dispose();
      }
    };
  },
};

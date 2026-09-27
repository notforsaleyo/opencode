import { createOpenCode2TuiPlugin } from "./node_modules/opencode-codex-usage/dist/opencode2-tui.js";
import { createQuotaMonitor } from "./node_modules/opencode-codex-usage/dist/lib/codex-usage-monitor.js";

// Node's maximum supported interval: 24 days, 20 hours, 31 minutes, 23.647 seconds.
// Keep this customization separate from the installed upstream package.
const MAX_POLL_MS = 2_147_483_647;
export default {
  id: "opencode-codex-usage",
  setup(context) {
    let automaticMonitorCreated = false;
    const upstream = createOpenCode2TuiPlugin(undefined, (options) => {
      if (automaticMonitorCreated) return createQuotaMonitor(options);
      automaticMonitorCreated = true;
      return createQuotaMonitor({
        ...options,
        pollMs: MAX_POLL_MS,
        threshold: "never",
        notify: () => {},
      });
    });
    return upstream.setup({
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
  },
};

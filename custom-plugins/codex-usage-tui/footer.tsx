/** @jsxImportSource @opentui/solid */
import { batch, createSignal, Show } from "solid-js";
import { formatQuota } from "./format.js";

export function createQuotaFooter(context) {
  const [snapshot, setSnapshot] = createSignal();
  const [checkedAt, setCheckedAt] = createSignal(0);
  const [now, setNow] = createSignal(Date.now());
  const [loading, setLoading] = createSignal(false);
  const [failed, setFailed] = createSignal(false);
  let disposed = false;
  const text = () => {
    if (failed()) return "Codex · 조회 실패 (/codex-usage로 재시도)";
    const quota = formatQuota(snapshot(), checkedAt(), now());
    return loading() ? (quota ? `${quota} · 조회 중` : "Codex · 조회 중…") : quota;
  };
  // Only redraw the local countdown. This timer never makes a quota request.
  const clock = setInterval(() => setNow(Date.now()), 60000);
  const release = context.ui.slot({
    append: "prompt.footer.status",
    render: () => (
      <Show when={text()}>
        <text fg={context.theme.text.muted} wrapMode="none" truncate flexShrink={0} minWidth={0}>
          {text()}
        </text>
      </Show>
    ),
  });

  return {
    loading() {
      if (disposed) return;
      batch(() => {
        setFailed(false);
        setLoading(true);
      });
    },
    update(value) {
      if (disposed) return;
      const timestamp = Date.now();
      batch(() => {
        setSnapshot(value);
        setCheckedAt(timestamp);
        setNow(timestamp);
        setLoading(false);
        setFailed(false);
      });
    },
    fail() {
      if (disposed) return;
      batch(() => {
        setLoading(false);
        setFailed(true);
      });
    },
    dispose() {
      disposed = true;
      clearInterval(clock);
      release();
    },
  };
}

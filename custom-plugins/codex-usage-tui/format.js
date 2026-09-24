function windowLabel(minutes, fallback) {
  if (minutes === 10080) return "주간";
  if (!(minutes > 0)) return fallback;
  if (minutes % 1440 === 0) return `${minutes / 1440}d`;
  if (minutes % 60 === 0) return `${minutes / 60}h`;
  return `${minutes}m`;
}

function resetLabel(reset, checkedAt, now) {
  if (typeof reset !== "string" || !/^(?:\d+[dhm])+$/.test(reset)) return "";
  const units = { d: 86400000, h: 3600000, m: 60000 };
  const duration = [...reset.matchAll(/(\d+)([dhm])/g)].reduce(
    (total, [, amount, unit]) => total + Number(amount) * units[unit],
    0,
  );
  const minutes = Math.max(0, Math.ceil((checkedAt + duration - now) / 60000));
  if (minutes === 0) return "초기화 대기";
  if (minutes >= 1440) return `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h 후 초기화`;
  if (minutes >= 60) return `${Math.floor(minutes / 60)}h ${minutes % 60}m 후 초기화`;
  return `${minutes}m 후 초기화`;
}

export function formatQuota(snapshot, checkedAt, now = Date.now()) {
  if (!snapshot) return "";
  if (snapshot.error || snapshot.status === "error") return "Codex · 조회 실패 (/codex-usage로 재시도)";
  const windows = ["primary", "secondary"].flatMap((key, index) => {
    const used = snapshot.used?.[key];
    if (typeof used !== "number" || !Number.isFinite(used)) return [];
    const minutes = snapshot.windowMinutes?.[key];
    const reset = snapshot.reset?.[key];
    // Some plans return an unused second bucket with all fields set to zero.
    if (!(minutes > 0) && used === 0 && (!reset || reset === "0m")) return [];
    const remaining = Math.round(100 - Math.max(0, Math.min(100, used)));
    const countdown = resetLabel(reset, checkedAt, now);
    return [`${windowLabel(minutes, index === 0 ? "단기" : "장기")} ${remaining}% 남음${countdown ? ` (${countdown})` : ""}`];
  });
  return windows.length ? `Codex · ${windows.join(" · ")}` : "Codex · 한도 정보 없음";
}

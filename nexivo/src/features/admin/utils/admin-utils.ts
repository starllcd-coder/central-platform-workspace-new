export function getStatusBadgeVariant(status: string) {
  const map: Record<string, "success" | "warning" | "destructive" | "secondary" | "outline"> = {
    healthy: "success",
    warning: "warning",
    critical: "destructive",
    maintenance: "secondary",
    ready: "success",
    draft: "warning",
    planned: "secondary"
  };

  return map[status] ?? "outline";
}

export function getTrendLabel(trend: "up" | "down" | "stable") {
  const map = {
    up: "Increasing",
    down: "Decreasing",
    stable: "Stable"
  };

  return map[trend];
}

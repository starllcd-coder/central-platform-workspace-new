export function getPartnerProductLabel(product: string) {
  const map: Record<string, string> = {
    staylux: "StayLux",
    drivesphere: "DriveSphere",
    laundrex: "Laundrex"
  };

  return map[product] ?? product;
}

export function getPartnerProductBadgeVariant(product: string) {
  const map: Record<string, "default" | "luxury" | "gold"> = {
    staylux: "default",
    drivesphere: "luxury",
    laundrex: "gold"
  };

  return map[product] ?? "default";
}

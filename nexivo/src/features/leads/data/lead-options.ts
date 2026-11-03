export const productInterestOptions = [
  { value: "staylux", label: "StayLux — Hotels / Properties" },
  { value: "drivesphere", label: "DriveSphere — Car Rental" },
  { value: "laundrex", label: "Laundrex — Laundry Business" },
  { value: "central-platform", label: "DSS Central Platform" },
  { value: "multiple", label: "Multiple DSS Products" }
] as const;

export const businessSizeOptions = [
  { value: "small", label: "Small business / single branch" },
  { value: "medium", label: "Medium business / multiple branches" },
  { value: "enterprise", label: "Enterprise / group operation" },
  { value: "startup", label: "New business / startup" }
] as const;

export const businessTypeOptions = [
  "Hotel",
  "Rental Apartment",
  "Villa / Property Manager",
  "Car Rental Company",
  "Fleet Operator",
  "Laundry Shop",
  "Laundry Pickup & Delivery",
  "Multi-service Business",
  "Other"
] as const;

export type BusinessProductKey =
  | "staylux"
  | "drivesphere"
  | "laundrex"
  | "central-platform";

export type BusinessPricingModel = {
  product: string;
  setupFee: string;
  model: string;
  publicDisplay: string;
  privateNote: string;
};

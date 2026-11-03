export type PricingProduct = "staylux" | "drivesphere" | "laundrex";

export type PricingPlan = {
  id: string;
  product: PricingProduct;
  productName: string;
  title: string;
  setupFee: string;
  ongoingModel: string;
  publicDescription: string;
  highlights: string[];
  recommendedFor: string;
  exactCommissionVisible: boolean;
};

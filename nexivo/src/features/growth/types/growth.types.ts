export type LoyaltyTier = "bronze" | "silver" | "gold" | "platinum";

export type LoyaltyTierInfo = {
  tier: LoyaltyTier;
  title: string;
  requiredPoints: number;
  multiplier: string;
  benefits: string[];
};

export type CouponType = "percentage" | "fixed" | "free-delivery" | "upgrade";

export type Coupon = {
  id: string;
  code: string;
  title: string;
  description: string;
  type: CouponType;
  valueLabel: string;
  serviceScope: "all" | "stays" | "cars" | "laundry";
  expiryDate: string;
  active: boolean;
};

export type Promotion = {
  id: string;
  title: string;
  description: string;
  serviceScope: "stays" | "cars" | "laundry" | "business";
  location: string;
  badge: string;
  href: string;
  imageUrl: string;
};

export type SponsoredPlacement = {
  id: string;
  title: string;
  businessName: string;
  serviceScope: "stays" | "cars" | "laundry";
  placement: "homepage" | "search-top" | "destination-page" | "category-page";
  monthlyPriceLabel: string;
  status: "active" | "available" | "reserved";
};

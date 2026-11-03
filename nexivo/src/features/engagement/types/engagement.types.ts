export type ReviewServiceType = "stay" | "car" | "laundry";

export type VerifiedReview = {
  id: string;
  serviceType: ReviewServiceType;
  title: string;
  provider: string;
  customerName: string;
  rating: number;
  comment: string;
  date: string;
  verifiedBooking: boolean;
  imageUrl?: string;
};

export type WishlistItem = {
  id: string;
  serviceType: ReviewServiceType;
  title: string;
  location: string;
  imageUrl: string;
  href: string;
  priceLabel: string;
  rating: number;
};

export type ReferralReward = {
  id: string;
  type: "customer" | "business";
  title: string;
  description: string;
  reward: string;
  status: "active" | "future";
};

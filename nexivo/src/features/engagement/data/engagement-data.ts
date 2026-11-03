import type {
  ReferralReward,
  VerifiedReview,
  WishlistItem
} from "@/features/engagement/types/engagement.types";

export const verifiedReviews: VerifiedReview[] = [
  {
    id: "rev-001",
    serviceType: "stay",
    title: "Salalah Garden Suites",
    provider: "StayLux",
    customerName: "Ahmed K.",
    rating: 5,
    comment: "Clean apartment, smooth booking, and very convenient for Salalah family travel.",
    date: "May 2026",
    verifiedBooking: true,
    imageUrl: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop"
  },
  {
    id: "rev-002",
    serviceType: "car",
    title: "Toyota Corolla 2024",
    provider: "DriveSphere",
    customerName: "Maria S.",
    rating: 4,
    comment: "Pickup was quick, car was clean, and the deposit terms were clear.",
    date: "May 2026",
    verifiedBooking: true,
    imageUrl: "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=900&auto=format&fit=crop"
  },
  {
    id: "rev-003",
    serviceType: "laundry",
    title: "Salalah Fresh Laundry",
    provider: "Laundrex",
    customerName: "Omar A.",
    rating: 5,
    comment: "Pickup and delivery were on time. Useful service during travel.",
    date: "June 2026",
    verifiedBooking: true,
    imageUrl: "https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?q=80&w=900&auto=format&fit=crop"
  }
];

export const wishlistItems: WishlistItem[] = [
  {
    id: "wish-001",
    serviceType: "stay",
    title: "Dubai Marina Skyline Residence",
    location: "Dubai, UAE",
    imageUrl: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=900&auto=format&fit=crop",
    href: "/stays/dubai-marina-skyline-residence",
    priceLabel: "From AED 410 / night",
    rating: 4.8
  },
  {
    id: "wish-002",
    serviceType: "car",
    title: "Nissan Patrol 2024",
    location: "Muscat, Oman",
    imageUrl: "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?q=80&w=900&auto=format&fit=crop",
    href: "/cars/nissan-patrol-2024-muscat",
    priceLabel: "From OMR 45 / day",
    rating: 4.8
  },
  {
    id: "wish-003",
    serviceType: "laundry",
    title: "Muscat Premium Cleaners",
    location: "Muscat, Oman",
    imageUrl: "https://images.unsplash.com/photo-1604335399105-a0c585fd81a1?q=80&w=900&auto=format&fit=crop",
    href: "/laundry/providers/muscat-premium-cleaners",
    priceLabel: "Min OMR 4",
    rating: 4.6
  }
];

export const referralRewards: ReferralReward[] = [
  {
    id: "ref-001",
    type: "customer",
    title: "Customer Referral",
    description: "Invite friends to Nexivo and earn reward points after their first completed booking.",
    reward: "Up to 500 Nexivo points",
    status: "active"
  },
  {
    id: "ref-002",
    type: "business",
    title: "Business Referral",
    description: "Refer hotels, car rental companies, or laundry businesses to DSS and earn partner rewards.",
    reward: "Free promotion credit or reduced platform fee",
    status: "future"
  }
];

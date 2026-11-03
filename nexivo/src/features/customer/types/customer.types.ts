export type CustomerBookingType = "stay" | "car" | "laundry";

export type CustomerBookingStatus =
  | "confirmed"
  | "pending"
  | "completed"
  | "cancelled";

export type CustomerBooking = {
  id: string;
  type: CustomerBookingType;
  title: string;
  provider: string;
  location: string;
  dateLabel: string;
  amount: string;
  status: CustomerBookingStatus;
};

export type CustomerFavorite = {
  id: string;
  type: CustomerBookingType;
  title: string;
  location: string;
  imageUrl: string;
  href: string;
};

export type RewardActivity = {
  id: string;
  label: string;
  points: number;
  date: string;
};

export type CustomerDocument = {
  id: string;
  title: string;
  type: "passport" | "driving-license" | "id" | "other";
  status: "verified" | "pending" | "expired";
  updatedAt: string;
};

export type CustomerReview = {
  id: string;
  title: string;
  rating: number;
  comment: string;
  serviceType: CustomerBookingType;
  date: string;
};

export type CustomerNotification = {
  id: string;
  title: string;
  description: string;
  channel: "email" | "sms" | "whatsapp" | "push";
  date: string;
  read: boolean;
};

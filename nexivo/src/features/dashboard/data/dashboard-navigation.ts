import {
  Bell,
  BookOpenCheck,
  Building2,
  CalendarCheck2,
  CreditCard,
  FileText,
  Heart,
  LayoutDashboard,
  LifeBuoy,
  Settings,
  ShieldCheck,
  Star,
  Users,
  WalletCards
} from "lucide-react";

export const customerDashboardNavigation = [
  {
    label: "Overview",
    href: "/customer",
    icon: LayoutDashboard
  },
  {
    label: "Bookings",
    href: "/customer/bookings",
    icon: CalendarCheck2
  },
  {
    label: "Favorites",
    href: "/customer/favorites",
    icon: Heart
  },
  {
    label: "Rewards",
    href: "/customer/rewards",
    icon: Star
  },
  {
    label: "Documents",
    href: "/customer/documents",
    icon: FileText
  },
  {
    label: "Reviews",
    href: "/customer/reviews",
    icon: BookOpenCheck
  },
  {
    label: "Notifications",
    href: "/customer/notifications",
    icon: Bell
  },
  {
    label: "Settings",
    href: "/customer/settings",
    icon: Settings
  }
] as const;

export const partnerDashboardNavigation = [
  {
    label: "Overview",
    href: "/partner",
    icon: LayoutDashboard
  },
  {
    label: "Listings",
    href: "/partner/listings",
    icon: Building2
  },
  {
    label: "Bookings",
    href: "/partner/bookings",
    icon: CalendarCheck2
  },
  {
    label: "Billing",
    href: "/partner/billing",
    icon: WalletCards
  },
  {
    label: "Reports",
    href: "/partner/reports",
    icon: CreditCard
  },
  {
    label: "Staff",
    href: "/partner/staff",
    icon: Users
  },
  {
    label: "Support",
    href: "/partner/support",
    icon: LifeBuoy
  },
  {
    label: "Settings",
    href: "/partner/settings",
    icon: ShieldCheck
  }
] as const;

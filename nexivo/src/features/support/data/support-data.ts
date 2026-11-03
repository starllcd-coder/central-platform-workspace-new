export const supportFaqs = [
  {
    question: "Can customers book without registering first?",
    answer:
      "Yes. Customers can search first and account registration can happen during booking using their email."
  },
  {
    question: "Should card details be required for pay-at-hotel?",
    answer:
      "Yes, card guarantee can be required for pay-at-property or pay-at-pickup flows, but real card data must be handled by a secure payment gateway."
  },
  {
    question: "Should commission percentage be public?",
    answer:
      "No. Public website should show setup fee and commercial model only. Exact commission should be discussed after demo."
  },
  {
    question: "Can pricing change later?",
    answer:
      "Yes. Pricing, commissions, setup fees, subscriptions, promotions, and sponsored placements should remain configurable from DSS Central Platform."
  },
  {
    question: "Is Nexivo GCC-only?",
    answer:
      "The launch focus is GCC, but the structure is prepared for European languages, GDPR pages, currencies, and future expansion."
  }
] as const;

export const contactChannels = [
  {
    title: "Business demo",
    description: "For hotels, car rentals, laundry businesses, and DSS product demos.",
    href: "/business/request-demo"
  },
  {
    title: "Customer support",
    description: "For booking, rental, laundry, account, payment, and notification support.",
    href: "/support"
  },
  {
    title: "Partner portal",
    description: "For businesses already registered on Nexivo.",
    href: "/partner-login"
  }
] as const;

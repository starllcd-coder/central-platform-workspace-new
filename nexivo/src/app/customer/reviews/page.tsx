import { CustomerReviewsList } from "@/features/customer/components/customer-reviews-list";
import { customerReviews } from "@/features/customer/data/customer-dashboard-data";

export default function CustomerReviewsPage() {
  return <CustomerReviewsList reviews={customerReviews} />;
}

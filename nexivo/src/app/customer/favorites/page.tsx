import { CustomerFavoritesGrid } from "@/features/customer/components/customer-favorites-grid";
import { customerFavorites } from "@/features/customer/data/customer-dashboard-data";

export default function CustomerFavoritesPage() {
  return <CustomerFavoritesGrid favorites={customerFavorites} />;
}

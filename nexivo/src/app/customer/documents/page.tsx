import { CustomerDocumentsList } from "@/features/customer/components/customer-documents-list";
import { customerDocuments } from "@/features/customer/data/customer-dashboard-data";

export default function CustomerDocumentsPage() {
  return <CustomerDocumentsList documents={customerDocuments} />;
}

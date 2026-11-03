import { UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PartnerStaff } from "@/features/partner/types/partner.types";
import {
  getPartnerProductBadgeVariant,
  getPartnerProductLabel
} from "@/features/partner/components/partner-utils";

type PartnerStaffTableProps = {
  staff: PartnerStaff[];
};

export function PartnerStaffTable({ staff }: PartnerStaffTableProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Staff Management</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Partner staff access is prepared for role-based product access across StayLux, DriveSphere, and Laundrex.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {staff.map((member) => (
          <div
            key={member.id}
            className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft md:flex-row md:items-center md:justify-between"
          >
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <UserRound size={21} />
              </div>

              <div>
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                  {member.name}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {member.email} • {member.role}
                </p>

                <div className="mt-3 flex flex-wrap gap-2">
                  {member.productAccess.map((product) => (
                    <Badge key={product} variant={getPartnerProductBadgeVariant(product)}>
                      {getPartnerProductLabel(product)}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <Badge
              variant={
                member.status === "active"
                  ? "success"
                  : member.status === "invited"
                    ? "warning"
                    : "destructive"
              }
            >
              {member.status}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

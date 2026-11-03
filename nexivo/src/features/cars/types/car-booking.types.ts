import type { RentalVehicle } from "@/features/cars/types/cars.types";

export type CarBookingDraft = {
  vehicleId: string;
  pickupDate: string;
  returnDate: string;
  pickupLocation: string;
  returnLocation: string;
  rentalDays: number;
  driverName?: string;
  driverEmail?: string;
  driverPhone?: string;
  driverLicenseNumber?: string;
  paymentMethod?: "pay-online" | "pay-at-pickup";
  cardGuaranteeRequired?: boolean;
};

export type VehiclePolicy = {
  vehicleId: string;
  minimumAge: number;
  depositRequired: boolean;
  mileagePolicy: string;
  fuelPolicy: string;
  insurancePolicy: string;
  cancellationPolicy: string;
  documentsRequired: string[];
  settlementCurrency: RentalVehicle["currency"];
};

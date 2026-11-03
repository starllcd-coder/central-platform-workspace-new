import type { VehiclePolicy } from "@/features/cars/types/car-booking.types";

export const vehiclePolicies: VehiclePolicy[] = [
  {
    vehicleId: "car-001",
    minimumAge: 21,
    depositRequired: true,
    mileagePolicy: "250 km per day included.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Standard insurance included. Excess may apply.",
    cancellationPolicy: "Free cancellation up to 24 hours before pickup.",
    documentsRequired: ["Passport or ID", "Driving license", "Valid card for guarantee"],
    settlementCurrency: "OMR"
  },
  {
    vehicleId: "car-002",
    minimumAge: 25,
    depositRequired: true,
    mileagePolicy: "300 km per day included.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Full insurance package available.",
    cancellationPolicy: "Free cancellation up to 48 hours before pickup.",
    documentsRequired: ["Passport or ID", "Driving license", "Valid card for guarantee"],
    settlementCurrency: "OMR"
  },
  {
    vehicleId: "car-003",
    minimumAge: 21,
    depositRequired: true,
    mileagePolicy: "200 km per day included.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Basic insurance included.",
    cancellationPolicy: "Free cancellation up to 24 hours before pickup.",
    documentsRequired: ["Passport or Emirates ID", "Driving license", "Credit card"],
    settlementCurrency: "AED"
  },
  {
    vehicleId: "car-004",
    minimumAge: 25,
    depositRequired: true,
    mileagePolicy: "200 km per day included.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Premium insurance available on request.",
    cancellationPolicy: "Non-refundable promotional luxury rate.",
    documentsRequired: ["Passport or Qatar ID", "Driving license", "Credit card"],
    settlementCurrency: "QAR"
  },
  {
    vehicleId: "car-005",
    minimumAge: 23,
    depositRequired: true,
    mileagePolicy: "250 km per day included.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Standard insurance included.",
    cancellationPolicy: "Free cancellation up to 24 hours before pickup.",
    documentsRequired: ["Passport or Saudi ID", "Driving license", "Valid card"],
    settlementCurrency: "SAR"
  },
  {
    vehicleId: "car-006",
    minimumAge: 25,
    depositRequired: true,
    mileagePolicy: "Unlimited mileage for selected routes.",
    fuelPolicy: "Return with same fuel level.",
    insurancePolicy: "Full insurance recommended for scenic and desert routes.",
    cancellationPolicy: "Free cancellation up to 48 hours before pickup.",
    documentsRequired: ["Passport or Saudi ID", "Driving license", "Valid card"],
    settlementCurrency: "SAR"
  }
];

export function getVehiclePolicy(vehicleId: string): VehiclePolicy | undefined {
  return vehiclePolicies.find((policy) => policy.vehicleId === vehicleId);
}

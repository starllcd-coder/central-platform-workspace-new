import { stayProperties } from "@/features/stays/data/stay-properties";
import { rentalVehicles } from "@/features/cars/data/rental-vehicles";
import { laundryProviders } from "@/features/laundry/data/laundry-providers";
import { pricingPlans } from "@/features/pricing/data/pricing-data";
import { coupons, promotions, sponsoredPlacements } from "@/features/growth/data/growth-data";
import { integrationConnectors } from "@/features/integrations/data/integration-connectors";

export const mockCentralPlatformSnapshot = {
  generatedAt: new Date().toISOString(),
  products: {
    staylux: {
      listings: stayProperties.length,
      active: stayProperties.filter((item) => item.verified).length
    },
    drivesphere: {
      listings: rentalVehicles.length,
      active: rentalVehicles.filter((item) => item.verified).length
    },
    laundrex: {
      listings: laundryProviders.length,
      active: laundryProviders.filter((item) => item.verified).length
    }
  },
  commercial: {
    pricingPlans: pricingPlans.length,
    coupons: coupons.length,
    promotions: promotions.length,
    sponsoredPlacements: sponsoredPlacements.length
  },
  integrations: {
    total: integrationConnectors.length,
    requiredForLaunch: integrationConnectors.filter((item) => item.requiredForLaunch).length,
    mock: integrationConnectors.filter((item) => item.status === "mock").length,
    planned: integrationConnectors.filter((item) => item.status === "planned").length
  }
};

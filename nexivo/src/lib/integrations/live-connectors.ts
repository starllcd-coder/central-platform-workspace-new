import { integrationConnectors } from "@/features/integrations/data/integration-connectors";
import type { IntegrationStatus } from "@/features/integrations/types/integration.types";
import { centralPlatformFallbackEnabled, centralPlatformRequest } from "./central-platform-api";
export async function getLiveConnectors() {
  try {
    const result=await centralPlatformRequest<{statuses:Record<string,IntegrationStatus>}>("/capabilities/");
    return integrationConnectors.map(connector=>({...connector,status:result.statuses[connector.module] || "planned" as IntegrationStatus}));
  }catch{
    return integrationConnectors.map(connector=>({...connector,status:centralPlatformFallbackEnabled()?connector.status:"error" as IntegrationStatus}));
  }
}

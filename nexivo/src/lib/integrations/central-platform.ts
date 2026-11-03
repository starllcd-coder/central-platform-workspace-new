import { integrationConnectors } from "@/features/integrations/data/integration-connectors";
import type {
  CentralPlatformModule,
  CentralSyncPayload,
  IntegrationConnector
} from "@/features/integrations/types/integration.types";

export function getConnectorByModule(
  module: CentralPlatformModule
): IntegrationConnector | undefined {
  return integrationConnectors.find((connector) => connector.module === module);
}

export async function mockCentralPlatformSync(payload: CentralSyncPayload) {
  return {
    syncId: `sync_${Date.now()}`,
    entity: payload.entity,
    action: payload.action,
    records: payload.records,
    status: "completed",
    completedAt: new Date().toISOString()
  };
}

export function isLaunchReadyConnector(connector: IntegrationConnector) {
  if (!connector.requiredForLaunch) return true;

  return connector.status === "connected";
}

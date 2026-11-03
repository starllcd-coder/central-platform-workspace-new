import { AppLaunchReturn } from "@/features/partner/components/app-launch-return";
export default async function AppLaunchPage({searchParams}:{searchParams:Promise<{state?:string;tenantCode?:string;moduleCode?:string}>}) {
  const params=await searchParams;
  return <AppLaunchReturn state={params.state||""} tenantCode={params.tenantCode||""} moduleCode={params.moduleCode||""} />;
}

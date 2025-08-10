import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./app-sidebar";

export function Dashboard() {
  return (
    <SidebarProvider>
      <div className="flex h-screen bg-background">
        <AppSidebar />
        <div className="flex-1 flex flex-col">
          <header className="border-b p-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <h1 className="text-lg font-semibold">ダッシュボード</h1>
            </div>
          </header>
          <main className="flex-1 p-4">
            <p>ダッシュボードの内容</p>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}

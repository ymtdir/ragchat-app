import React, { useEffect, useState } from "react";
import { UserTable, type User } from "@/components/user-table";
import { UserService } from "@/services/user-service";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCw } from "lucide-react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./app-sidebar";

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await UserService.getAllUsers();
      setUsers(data);
    } catch (err) {
      console.error("ユーザー取得エラー:", err);
      setError("ユーザーの取得に失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRefresh = () => {
    fetchUsers();
  };

  const handleAddUser = () => {
    // TODO: ユーザー追加機能を実装
    console.log("ユーザー追加");
  };

  const renderContent = () => {
    if (error) {
      return (
        <div className="flex justify-center">
          <Card className="max-w-2xl">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-red-600 mb-4">{error}</p>
                <Button onClick={handleRefresh} variant="outline">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  再試行
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return (
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">ユーザー一覧</h1>
            <p className="text-muted-foreground">
              システム内のユーザーを一覧表示します。
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={handleAddUser} size="sm">
              <Plus className="mr-2 h-4 w-4" />
              ユーザー追加
            </Button>
          </div>
        </div>
        <UserTable data={users} isLoading={isLoading} />
      </div>
    );
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen bg-background">
        <AppSidebar />
        <div className="flex-1 flex flex-col">
          <header className="border-b p-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <h1 className="text-lg font-semibold">ユーザー管理</h1>
            </div>
          </header>
          <main className="flex-1 p-6 overflow-auto">{renderContent()}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}

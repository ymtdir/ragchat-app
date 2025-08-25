import { useEffect, useState } from "react";
import { UserTable } from "@/components/user-table";
import type { User } from "@/types/api";
import { UserService } from "@/services/user-service";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Plus, AlertCircle } from "lucide-react";
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
      console.error("ユーザー情報の取得に失敗:", err);
      setError("ユーザー情報の読み込みに失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleAddUser = () => {
    // TODO: ユーザー追加機能を実装
    console.log("ユーザー追加");
  };

  const handleUserUpdate = (updatedUser: User) => {
    // ユーザー情報が更新されたら、テーブルを再読み込み
    setUsers((prevUsers) =>
      prevUsers.map((user) => (user.id === updatedUser.id ? updatedUser : user))
    );
  };

  const renderContent = () => {
    if (error) {
      return (
        <div className="space-y-4">
          <Alert variant="destructive" className="text-left">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>ユーザー情報の読み込みに失敗しました</AlertTitle>
            <AlertDescription>
              <p className="my-1">
                データの取得中にエラーが発生しました。以下の原因が考えられます：
              </p>
              <ul className="list-inside list-disc text-sm my-1 pl-4">
                <li>データベース接続エラー</li>
                <li>APIサーバーの一時的な問題</li>
                <li>ネットワーク接続の不具合</li>
                <li>認証トークンの有効期限切れ</li>
              </ul>
            </AlertDescription>
          </Alert>
        </div>
      );
    }

    return (
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-left">
              ユーザー管理
            </h1>
            <p className="text-muted-foreground">
              登録ユーザーの管理と詳細情報を確認できます。
            </p>
          </div>
          <div className="flex items-center space-x-1">
            <Button onClick={handleAddUser} size="sm">
              <Plus className="h-4 w-4" />
              新規ユーザー
            </Button>
          </div>
        </div>
        <UserTable
          data={users}
          isLoading={isLoading}
          onUserUpdate={handleUserUpdate}
        />
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

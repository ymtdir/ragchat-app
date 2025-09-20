import { useEffect, useState } from "react";
import { GroupTable } from "@/components/group/group-table";
import { GroupCreateModal } from "@/components/group/group-create-modal";
import { GroupMemberManagementModal } from "@/components/group/group-member-management-modal";
import type { Group } from "@/types/api";
import { GroupService } from "@/services/group-service";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Plus, AlertCircle } from "lucide-react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";

export function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isMemberManagementModalOpen, setIsMemberManagementModalOpen] = useState(false);
  const [selectedGroupForMemberManagement, setSelectedGroupForMemberManagement] = useState<Group | null>(null);

  const fetchGroups = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await GroupService.getAllGroups();
      setGroups(data);
    } catch (err) {
      console.error("グループ情報の取得に失敗:", err);
      setError("グループ情報の読み込みに失敗しました。");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleAddGroup = () => {
    setIsCreateModalOpen(true);
  };

  const handleGroupUpdate = (updatedGroup: Group) => {
    // グループ情報が更新されたら、テーブルを再読み込み
    setGroups(prevGroups =>
      prevGroups.map(group =>
        group.id === updatedGroup.id ? updatedGroup : group
      )
    );
  };

  const handleGroupCreate = (newGroup: Group) => {
    // 新しいグループが作成されたら、テーブルに追加
    setGroups(prevGroups => [...prevGroups, newGroup]);
  };

  const handleGroupDelete = (groupId: number) => {
    // グループが削除されたら、テーブルから削除
    setGroups(prevGroups => prevGroups.filter(group => group.id !== groupId));
  };

  const handleBulkGroupDelete = (groupIds: number[]) => {
    // 複数のグループが削除されたら、テーブルから削除
    setGroups(prevGroups =>
      prevGroups.filter(group => !groupIds.includes(group.id))
    );
  };

  const handleManageMembers = (group: Group) => {
    setSelectedGroupForMemberManagement(group);
    setIsMemberManagementModalOpen(true);
  };

  const handleCloseMemberManagement = () => {
    setIsMemberManagementModalOpen(false);
    setSelectedGroupForMemberManagement(null);
  };

  const handleMembershipChange = () => {
    // メンバーシップが変更されたら、UI を更新する必要がある場合は
    // ここで処理を行う（例：グループ一覧の再読み込み）
    // 現在は特に何もしないが、将来的にはメンバー数の更新などを行う可能性がある
  };

  const renderContent = () => {
    if (error) {
      return (
        <div className="space-y-4">
          <Alert variant="destructive" className="text-left">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>グループ情報の読み込みに失敗しました</AlertTitle>
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
              グループ管理
            </h1>
            <p className="text-muted-foreground">
              登録グループの管理と詳細情報を確認できます。
            </p>
          </div>
          <div className="flex items-center space-x-1">
            <Button onClick={handleAddGroup} size="sm">
              <Plus className="h-4 w-4" />
              新規グループ
            </Button>
          </div>
        </div>
        <GroupTable
          data={groups}
          isLoading={isLoading}
          onGroupUpdate={handleGroupUpdate}
          onGroupDelete={handleGroupDelete}
          onBulkGroupDelete={handleBulkGroupDelete}
          onManageMembers={handleManageMembers}
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
              <h1 className="text-lg font-semibold">グループ管理</h1>
            </div>
          </header>
          <main className="flex-1 p-6 overflow-auto">{renderContent()}</main>
        </div>
      </div>
      <GroupCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSave={handleGroupCreate}
      />
      <GroupMemberManagementModal
        group={selectedGroupForMemberManagement}
        isOpen={isMemberManagementModalOpen}
        onClose={handleCloseMemberManagement}
        onMembershipChange={handleMembershipChange}
      />
    </SidebarProvider>
  );
}

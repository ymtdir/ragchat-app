/**
 * グループメンバー管理モーダル
 *
 * グループのメンバー管理（表示、追加、削除）を行うモーダルコンポーネント
 */

import { useEffect, useState, useCallback } from "react";
import { Search, Plus, Trash2, Users, Loader2, UserPlus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MembershipService } from "@/services/membership-service";
import type { Group, User, Member } from "@/types/api";

interface GroupMemberManagementModalProps {
  group: Group | null;
  isOpen: boolean;
  onClose: () => void;
  onMembershipChange?: () => void;
}

export function GroupMemberManagementModal({
  group,
  isOpen,
  onClose,
  onMembershipChange,
}: GroupMemberManagementModalProps) {
  // 現在のメンバー一覧
  const [currentMembers, setCurrentMembers] = useState<Member[]>([]);
  const [isLoadingMembers, setIsLoadingMembers] = useState(false);

  // 利用可能なユーザー一覧（追加用）
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);

  // UI状態
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUserIds, setSelectedUserIds] = useState<Set<number>>(
    new Set()
  );
  const [selectedMemberIds, setSelectedMemberIds] = useState<Set<number>>(
    new Set()
  );
  const [isAddingMembers, setIsAddingMembers] = useState(false);
  const [isRemovingMembers, setIsRemovingMembers] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // メンバー一覧を取得
  const fetchMembers = useCallback(async () => {
    if (!group) return;

    try {
      setIsLoadingMembers(true);
      setError(null);
      const membersResponse = await MembershipService.getGroupMembers(group.id);
      setCurrentMembers(membersResponse.members || []);
    } catch (err) {
      console.error("メンバー一覧の取得に失敗:", err);
      setError(
        `メンバー一覧の取得に失敗しました: ${err instanceof Error ? err.message : String(err)}`
      );
      setCurrentMembers([]);
    } finally {
      setIsLoadingMembers(false);
    }
  }, [group]);

  // 利用可能なユーザー一覧を取得
  const fetchAvailableUsers = useCallback(async () => {
    try {
      setIsLoadingUsers(true);
      setError(null);
      const users = await MembershipService.getAvailableUsers();
      setAvailableUsers(users);
    } catch (err) {
      console.error("ユーザー一覧の取得に失敗:", err);
      setError(
        `ユーザー一覧の取得に失敗しました: ${err instanceof Error ? err.message : String(err)}`
      );
      setAvailableUsers([]);
    } finally {
      setIsLoadingUsers(false);
    }
  }, []);

  // モーダルが開かれた時の初期化
  useEffect(() => {
    if (isOpen && group) {
      fetchMembers();
      fetchAvailableUsers();
      setSearchTerm("");
      setSelectedUserIds(new Set());
      setSelectedMemberIds(new Set());
      setError(null);
    }
  }, [isOpen, group, fetchMembers, fetchAvailableUsers]);

  // 検索でフィルタリングされたユーザー一覧（現在のメンバーを除外）
  const filteredAvailableUsers = availableUsers.filter(user => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const isNotMember = !currentMembers.some(
      member => member.user_id === user.id
    );

    return matchesSearch && isNotMember;
  });

  // ユーザー選択/選択解除
  const handleUserSelect = (userId: number) => {
    const newSelected = new Set(selectedUserIds);
    if (newSelected.has(userId)) {
      newSelected.delete(userId);
    } else {
      newSelected.add(userId);
    }
    setSelectedUserIds(newSelected);
  };

  // メンバー選択/選択解除
  const handleMemberSelect = (userId: number) => {
    const newSelected = new Set(selectedMemberIds);
    if (newSelected.has(userId)) {
      newSelected.delete(userId);
    } else {
      newSelected.add(userId);
    }
    setSelectedMemberIds(newSelected);
  };

  // メンバー追加
  const handleAddMembers = async () => {
    if (!group || selectedUserIds.size === 0) return;

    try {
      setIsAddingMembers(true);
      setError(null);

      const userIdsArray = Array.from(selectedUserIds);

      await MembershipService.addMultipleMembersToGroup({
        group_id: group.id,
        user_ids: userIdsArray,
      });

      // 成功時は一覧を更新
      await fetchMembers();
      // ユーザー一覧も再取得（既にメンバーになったユーザーを除外するため）
      await fetchAvailableUsers();
      setSelectedUserIds(new Set());
      onMembershipChange?.();
    } catch (err) {
      console.error("メンバー追加に失敗:", err);
      setError(
        `メンバーの追加に失敗しました: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setIsAddingMembers(false);
    }
  };

  // メンバー削除
  const handleRemoveMembers = async () => {
    if (!group || selectedMemberIds.size === 0) return;

    try {
      setIsRemovingMembers(true);
      setError(null);

      const memberIdsArray = Array.from(selectedMemberIds);

      await MembershipService.removeMultipleMembersFromGroup({
        group_id: group.id,
        user_ids: memberIdsArray,
      });

      // 成功時は一覧を更新
      await fetchMembers();
      // ユーザー一覧も再取得（削除されたユーザーが追加可能になるため）
      await fetchAvailableUsers();
      setSelectedMemberIds(new Set());
      onMembershipChange?.();
    } catch (err) {
      console.error("メンバー削除に失敗:", err);
      setError(
        `メンバーの削除に失敗しました: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setIsRemovingMembers(false);
    }
  };

  const handleClose = () => {
    onClose();
    setSearchTerm("");
    setSelectedUserIds(new Set());
    setSelectedMemberIds(new Set());
    setError(null);
  };

  if (!group) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-7xl max-h-[90vh] flex flex-col p-6">
        <DialogHeader className="pb-6">
          <DialogTitle className="flex items-center gap-3 text-2xl">
            <Users className="h-7 w-7" />
            メンバー管理: {group.name}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="members" className="flex-1 flex flex-col min-h-0">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="members" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              現在のメンバー ({currentMembers.length})
            </TabsTrigger>
            <TabsTrigger value="add-users" className="flex items-center gap-2">
              <UserPlus className="h-4 w-4" />
              ユーザーを追加 ({filteredAvailableUsers.length})
            </TabsTrigger>
          </TabsList>

          {/* メンバー一覧タブ */}
          <TabsContent
            value="members"
            className="flex-1 flex flex-col min-h-0 mt-0"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">現在のメンバー</h3>
                <p className="text-muted-foreground">
                  {currentMembers.length}人が参加中
                </p>
              </div>
              {selectedMemberIds.size > 0 && (
                <Button
                  variant="destructive"
                  onClick={handleRemoveMembers}
                  disabled={isRemovingMembers}
                  className="px-6"
                >
                  {isRemovingMembers ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      削除中...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      選択した{selectedMemberIds.size}人を削除
                    </>
                  )}
                </Button>
              )}
            </div>

            <div className="flex-1 border rounded-lg overflow-hidden bg-background">
              {isLoadingMembers ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="h-12 w-12 animate-spin" />
                </div>
              ) : currentMembers.length === 0 ? (
                <div className="text-center text-muted-foreground py-16">
                  <Users className="h-16 w-16 mx-auto mb-6 opacity-50" />
                  <h4 className="text-lg font-medium mb-2">
                    メンバーがいません
                  </h4>
                  <p className="text-sm">
                    「ユーザーを追加」タブからメンバーを追加してください
                  </p>
                </div>
              ) : (
                <div className="overflow-y-auto h-full">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">選択</TableHead>
                        <TableHead className="w-16">ID</TableHead>
                        <TableHead>名前</TableHead>
                        <TableHead>メールアドレス</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {currentMembers.map(member => (
                        <TableRow
                          key={member.user_id}
                          className="hover:bg-muted/50"
                        >
                          <TableCell>
                            <Checkbox
                              checked={selectedMemberIds.has(member.user_id)}
                              onCheckedChange={() =>
                                handleMemberSelect(member.user_id)
                              }
                            />
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {member.user_id}
                          </TableCell>
                          <TableCell className="font-medium">
                            {member.user_name}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {member.user_email}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </TabsContent>

          {/* ユーザー追加タブ */}
          <TabsContent
            value="add-users"
            className="flex-1 flex flex-col min-h-0 mt-0"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">ユーザーを追加</h3>
                <p className="text-muted-foreground">
                  利用可能なユーザーから選択してメンバーに追加
                </p>
              </div>
              {selectedUserIds.size > 0 && (
                <Button
                  onClick={handleAddMembers}
                  disabled={isAddingMembers}
                  className="px-6"
                >
                  {isAddingMembers ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      追加中...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      {selectedUserIds.size}人を追加
                    </>
                  )}
                </Button>
              )}
            </div>

            <div className="relative mb-6">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="名前またはメールアドレスで検索..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="pl-12 h-12 text-base"
              />
            </div>

            <div className="flex-1 border rounded-lg overflow-hidden bg-background">
              {isLoadingUsers ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="h-12 w-12 animate-spin" />
                </div>
              ) : filteredAvailableUsers.length === 0 ? (
                <div className="text-center text-muted-foreground py-16">
                  <Search className="h-16 w-16 mx-auto mb-6 opacity-50" />
                  <h4 className="text-lg font-medium mb-2">
                    {searchTerm
                      ? "検索結果がありません"
                      : "追加可能なユーザーがいません"}
                  </h4>
                  {searchTerm && (
                    <p className="text-sm">
                      別のキーワードで検索してみてください
                    </p>
                  )}
                </div>
              ) : (
                <div className="overflow-y-auto h-full">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">選択</TableHead>
                        <TableHead className="w-16">ID</TableHead>
                        <TableHead>名前</TableHead>
                        <TableHead>メールアドレス</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredAvailableUsers.map(user => (
                        <TableRow key={user.id} className="hover:bg-muted/50">
                          <TableCell>
                            <Checkbox
                              checked={selectedUserIds.has(user.id)}
                              onCheckedChange={() => handleUserSelect(user.id)}
                            />
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {user.id}
                          </TableCell>
                          <TableCell className="font-medium">
                            {user.name}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {user.email}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end pt-4 border-t">
          <Button variant="outline" onClick={handleClose} size="lg">
            閉じる
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

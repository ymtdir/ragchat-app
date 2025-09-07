import * as React from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import type { User } from "@/types/api";

interface UserBulkDeleteDialogProps {
  selectedUsers: User[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (success: boolean) => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function UserBulkDeleteDialog({
  selectedUsers,
  isOpen,
  onClose,
  onConfirm,
  onLoadingChange,
}: UserBulkDeleteDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleBulkDelete = async () => {
    if (selectedUsers.length === 0) return;

    setIsLoading(true);
    onLoadingChange?.(true);

    try {
      // 各ユーザーを順次削除
      const deletePromises = selectedUsers.map((user) =>
        fetch(`http://localhost:8000/api/users/${user.id}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        })
      );

      const responses = await Promise.all(deletePromises);

      // 全ての削除が成功したかチェック
      const allSuccessful = responses.every((response) => response.ok);

      if (allSuccessful) {
        console.log(
          "一括削除成功:",
          selectedUsers.length,
          "件のユーザーを削除しました"
        );
        onConfirm(true);
      } else {
        console.error("一括削除エラー: 一部のユーザーの削除に失敗しました");
        onConfirm(false);
      }
    } catch (error) {
      console.error("一括削除エラー:", error);
      onConfirm(false);
    } finally {
      setIsLoading(false);
      onLoadingChange?.(false);
    }
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>選択したユーザーを一括削除</AlertDialogTitle>
          <AlertDialogDescription>
            選択した {selectedUsers.length} 件のユーザーを削除しますか？
            <br />
            <br />
            <strong>削除対象:</strong>
            <br />
            {selectedUsers.map((user) => (
              <React.Fragment key={user.id}>
                • {user.name} (ID: {user.id})
                <br />
              </React.Fragment>
            ))}
            <br />
            この操作は取り消すことができません。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>キャンセル</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleBulkDelete}
            disabled={isLoading}
            className="bg-red-600 hover:bg-red-700 focus:ring-red-600 text-white"
          >
            {isLoading ? "削除中..." : `${selectedUsers.length}件を削除`}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

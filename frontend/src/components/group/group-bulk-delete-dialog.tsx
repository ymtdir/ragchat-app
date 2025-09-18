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
import type { Group } from "@/types/api";
import { GroupService } from "@/services/group-service";

interface GroupBulkDeleteDialogProps {
  selectedGroups: Group[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (success: boolean) => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function GroupBulkDeleteDialog({
  selectedGroups,
  isOpen,
  onClose,
  onConfirm,
  onLoadingChange,
}: GroupBulkDeleteDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleBulkDelete = async () => {
    if (selectedGroups.length === 0) return;

    setIsLoading(true);
    onLoadingChange?.(true);

    try {
      // 各グループを順次削除
      const deletePromises = selectedGroups.map(group =>
        GroupService.deleteGroup(group.id)
      );

      await Promise.all(deletePromises);

      console.log(
        "一括削除成功:",
        selectedGroups.length,
        "件のグループを削除しました"
      );
      onConfirm(true);
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
          <AlertDialogTitle>選択したグループを一括削除</AlertDialogTitle>
          <AlertDialogDescription>
            選択した {selectedGroups.length} 件のグループを削除しますか？
            <br />
            <br />
            <strong>削除対象:</strong>
            <br />
            {selectedGroups.map(group => (
              <React.Fragment key={group.id}>
                • {group.name} (ID: {group.id})
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
            {isLoading ? "削除中..." : `${selectedGroups.length}件を削除`}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

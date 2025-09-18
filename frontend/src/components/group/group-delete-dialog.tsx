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

interface GroupDeleteDialogProps {
  group: Group | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (success: boolean) => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function GroupDeleteDialog({
  group,
  isOpen,
  onClose,
  onConfirm,
  onLoadingChange,
}: GroupDeleteDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleDelete = async () => {
    if (!group) return;

    setIsLoading(true);
    onLoadingChange?.(true);

    try {
      await GroupService.deleteGroup(group.id);
      console.log("削除成功:", group.name);
      onConfirm(true);
    } catch (error) {
      console.error("削除エラー:", error);
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
          <AlertDialogTitle>グループを削除</AlertDialogTitle>
          <AlertDialogDescription>
            グループ "{group?.name}" を削除しますか？
            <br />
            この操作は取り消すことができません。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>キャンセル</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            disabled={isLoading}
            className="bg-red-600 hover:bg-red-700 focus:ring-red-600 text-white"
          >
            {isLoading ? "削除中..." : "削除"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

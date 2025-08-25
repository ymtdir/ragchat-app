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

interface UserDeleteDialogProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (success: boolean) => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function UserDeleteDialog({
  user,
  isOpen,
  onClose,
  onConfirm,
  onLoadingChange,
}: UserDeleteDialogProps) {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleDelete = async () => {
    if (!user) return;

    setIsLoading(true);
    onLoadingChange?.(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/users/${user.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log("削除成功:", result);
        onConfirm(true);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error(
          "削除エラー:",
          response.status,
          response.statusText,
          errorData
        );
        onConfirm(false);
      }
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
          <AlertDialogTitle>ユーザーを削除</AlertDialogTitle>
          <AlertDialogDescription>
            ユーザー "{user?.name}" を削除しますか？
            <br />
            この操作は取り消すことができません。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>キャンセル</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            disabled={isLoading}
            className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
          >
            {isLoading ? "削除中..." : "削除"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

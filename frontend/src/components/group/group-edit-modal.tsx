import * as React from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Group } from "@/types/api";
import { GroupService } from "@/services/group-service";

interface GroupEditModalProps {
  group: Group | null;
  isOpen: boolean;
  onClose: () => void;
  onSave?: (group: Group) => void;
}

export function GroupEditModal({
  group,
  isOpen,
  onClose,
  onSave,
}: GroupEditModalProps) {
  const [formData, setFormData] = React.useState({
    name: "",
    description: "",
  });

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // グループデータが変更されたときにフォームを更新
  React.useEffect(() => {
    if (group) {
      setFormData({
        name: group.name,
        description: group.description || "",
      });
    }
    setError(null);
  }, [group]);

  const handleSave = async () => {
    if (!group) return;

    setIsLoading(true);
    setError(null);

    try {
      // 更新するデータを準備
      const updateData: Record<string, string> = {};

      // 名前または説明が変更されている場合
      if (
        formData.name !== group.name ||
        formData.description !== (group.description || "")
      ) {
        if (formData.name !== group.name) updateData.name = formData.name;
        if (formData.description !== (group.description || "")) {
          updateData.description = formData.description || "";
        }
      }

      // 名前のバリデーション
      if (!formData.name || formData.name.length < 1) {
        throw new Error("グループ名を入力してください");
      }

      if (formData.name.length > 100) {
        throw new Error("グループ名は100文字以内で入力してください");
      }

      // 更新するデータがない場合は何もしない
      if (Object.keys(updateData).length === 0) {
        onClose();
        return;
      }

      // APIを呼び出してグループ情報を更新
      const updatedGroup = await GroupService.updateGroup(group.id, updateData);

      // 成功時の処理
      if (onSave) {
        onSave(updatedGroup);
      }

      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (!group) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="max-w-2xl"
        aria-describedby="group-edit-description"
      >
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">グループ編集</DialogTitle>
          <p
            id="group-edit-description"
            className="text-sm text-muted-foreground"
          >
            グループの情報を編集できます。
          </p>
        </DialogHeader>
        <div className="flex w-full flex-col gap-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <div className="whitespace-pre-line">{error}</div>
            </div>
          )}
          <Card>
            <CardHeader>
              <CardTitle>グループ情報</CardTitle>
              <CardDescription>
                グループ情報を変更します。
                <br />
                完了したら保存をクリックしてください。
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6">
              <div className="grid gap-3">
                <Label htmlFor="name">グループ名 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={e => handleInputChange("name", e.target.value)}
                  disabled={isLoading}
                  maxLength={100}
                />
              </div>
              <div className="grid gap-3">
                <Label htmlFor="description">説明（任意）</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={e =>
                    handleInputChange("description", e.target.value)
                  }
                  disabled={isLoading}
                  rows={3}
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            キャンセル
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? "保存中..." : "保存"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

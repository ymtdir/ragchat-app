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

interface GroupCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: (group: Group) => void;
}

export function GroupCreateModal({
  isOpen,
  onClose,
  onSave,
}: GroupCreateModalProps) {
  const [formData, setFormData] = React.useState({
    name: "",
    description: "",
  });

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // モーダルが開かれたときにフォームをリセット
  React.useEffect(() => {
    if (isOpen) {
      setFormData({
        name: "",
        description: "",
      });
      setError(null);
    }
  }, [isOpen]);

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // バリデーション
      if (!formData.name || formData.name.length < 1) {
        throw new Error("グループ名を入力してください");
      }

      if (formData.name.length > 100) {
        throw new Error("グループ名は100文字以内で入力してください");
      }

      // APIを呼び出してグループを作成
      const newGroup = await GroupService.createGroup({
        name: formData.name,
        description: formData.description || undefined,
      });

      // 成功時の処理
      if (onSave) {
        onSave(newGroup);
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="max-w-2xl"
        aria-describedby="group-create-description"
      >
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">グループ作成</DialogTitle>
          <p
            id="group-create-description"
            className="text-sm text-muted-foreground"
          >
            新しいグループの情報を入力してください。
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
                新しいグループの情報を入力します。
                <br />
                完了したら作成をクリックしてください。
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
                  placeholder="グループ名を入力"
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
                  placeholder="グループの説明を入力"
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
            {isLoading ? "作成中..." : "作成"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

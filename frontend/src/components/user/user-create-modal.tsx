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
import type { User } from "@/types/api";

interface UserCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: (user: User) => void;
}

export function UserCreateModal({
  isOpen,
  onClose,
  onSave,
}: UserCreateModalProps) {
  const [formData, setFormData] = React.useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // モーダルが開かれたときにフォームをリセット
  React.useEffect(() => {
    if (isOpen) {
      setFormData({
        name: "",
        email: "",
        password: "",
        confirm_password: "",
      });
      setError(null);
    }
  }, [isOpen]);

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // バリデーション
      if (!formData.name || formData.name.length < 3) {
        throw new Error("名前は3文字以上で入力してください");
      }

      if (!formData.email) {
        throw new Error("メールアドレスを入力してください");
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        throw new Error("有効なメールアドレスを入力してください");
      }

      if (!formData.password) {
        throw new Error("パスワードを入力してください");
      }

      if (formData.password.length < 8) {
        throw new Error("パスワードは8文字以上で入力してください");
      }

      if (formData.password !== formData.confirm_password) {
        throw new Error("パスワードが一致しません");
      }

      // APIを呼び出してユーザーを作成
      const response = await fetch("/api/users/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "ユーザーの作成に失敗しました");
      }

      const newUser = await response.json();

      // 成功時の処理
      if (onSave) {
        onSave(newUser);
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
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">ユーザー作成</DialogTitle>
        </DialogHeader>
        <div className="flex w-full flex-col gap-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <div className="whitespace-pre-line">{error}</div>
            </div>
          )}
          <Card>
            <CardHeader>
              <CardTitle>ユーザー情報</CardTitle>
              <CardDescription>
                新しいユーザーの情報を入力します。
                <br />
                完了したら作成をクリックしてください。
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6">
              <div className="grid gap-3">
                <Label htmlFor="name">名前</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={e => handleInputChange("name", e.target.value)}
                  disabled={isLoading}
                  placeholder="ユーザー名を入力"
                />
              </div>
              <div className="grid gap-3">
                <Label htmlFor="email">メールアドレス</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={e => handleInputChange("email", e.target.value)}
                  disabled={isLoading}
                  placeholder="example@example.com"
                />
              </div>
              <div className="grid gap-3">
                <Label htmlFor="password">パスワード</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={e => handleInputChange("password", e.target.value)}
                  disabled={isLoading}
                  placeholder="8文字以上で入力"
                />
              </div>
              <div className="grid gap-3">
                <Label htmlFor="confirm">パスワード（確認）</Label>
                <Input
                  id="confirm"
                  type="password"
                  value={formData.confirm_password}
                  onChange={e =>
                    handleInputChange("confirm_password", e.target.value)
                  }
                  disabled={isLoading}
                  placeholder="パスワードを再入力"
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

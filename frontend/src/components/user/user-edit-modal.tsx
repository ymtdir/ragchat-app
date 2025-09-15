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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { User } from "@/types/api";

interface UserEditModalProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onSave?: (user: User) => void;
}

export function UserEditModal({
  user,
  isOpen,
  onClose,
  onSave,
}: UserEditModalProps) {
  const [formData, setFormData] = React.useState({
    name: "",
    email: "",
  });

  const [passwordData, setPasswordData] = React.useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // ユーザーデータが変更されたときにフォームを更新
  React.useEffect(() => {
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
      });
    }
    // パスワードフォームをリセット
    setPasswordData({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });
    setError(null);
  }, [user]);

  const handleSave = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      // 更新するデータを準備
      const updateData: Record<string, string> = {};

      // 名前またはメールアドレスが変更されている場合
      if (formData.name !== user.name || formData.email !== user.email) {
        if (formData.name !== user.name) updateData.name = formData.name;
        if (formData.email !== user.email) updateData.email = formData.email;
      }

      // 名前のバリデーション
      if (formData.name && formData.name.length < 3) {
        throw new Error("名前は3文字以上で入力してください");
      }

      // メールアドレスの基本的なバリデーション
      if (
        formData.email &&
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
      ) {
        throw new Error("有効なメールアドレスを入力してください");
      }

      // パスワードのバリデーション（新しいパスワードが入力されている場合のみ）
      if (passwordData.new_password) {
        // 新しいパスワードの要件チェックを先に行う
        if (passwordData.new_password.length < 8) {
          throw new Error("新しいパスワードは8文字以上で入力してください");
        }

        if (!passwordData.current_password) {
          throw new Error("現在のパスワードを入力してください");
        }

        if (passwordData.new_password !== passwordData.confirm_password) {
          throw new Error("新しいパスワードが一致しません");
        }

        updateData.current_password = passwordData.current_password;
        updateData.new_password = passwordData.new_password;
      }

      // 更新するデータがない場合は何もしない
      if (Object.keys(updateData).length === 0) {
        onClose();
        return;
      }

      // APIを呼び出してユーザー情報を更新
      const response = await fetch(`/api/users/${user.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        const errorData = await response.json();

        // バリデーションエラーの場合（422エラー）
        if (response.status === 422 && errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // 複数のバリデーションエラーがある場合
            const errorMessages = errorData.detail
              .map((error: { loc?: string[]; msg: string }) => {
                // フィールド名を日本語に変換
                const fieldName = error.loc?.join(".") || "";
                let japaneseFieldName = "";
                if (fieldName.includes("name")) japaneseFieldName = "名前";
                else if (fieldName.includes("email"))
                  japaneseFieldName = "メールアドレス";
                else if (fieldName.includes("current_password"))
                  japaneseFieldName = "現在のパスワード";
                else if (fieldName.includes("new_password"))
                  japaneseFieldName = "新しいパスワード";
                else japaneseFieldName = fieldName;

                // エラーメッセージを日本語に変換
                let japaneseMessage = error.msg;
                if (error.msg.includes("at least 3 characters")) {
                  japaneseMessage = "3文字以上で入力してください";
                } else if (error.msg.includes("not a valid email address")) {
                  japaneseMessage = "有効なメールアドレスを入力してください";
                } else if (error.msg.includes("at least 8 characters")) {
                  japaneseMessage = "8文字以上で入力してください";
                }

                return `${japaneseFieldName}: ${japaneseMessage}`;
              })
              .join("\n");
            throw new Error(errorMessages);
          } else {
            throw new Error(errorData.detail);
          }
        }

        // その他のエラーの場合
        throw new Error(errorData.detail || "ユーザー情報の更新に失敗しました");
      }

      const updatedUser = await response.json();

      // 成功時の処理
      if (onSave) {
        onSave(updatedUser);
      }

      // パスワードフォームをリセット
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });

      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (!user) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">ユーザー編集</DialogTitle>
        </DialogHeader>
        <div className="flex w-full flex-col gap-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <div className="whitespace-pre-line">{error}</div>
            </div>
          )}
          <Tabs defaultValue="account" className="w-full">
            <TabsList>
              <TabsTrigger value="account">アカウント</TabsTrigger>
              <TabsTrigger value="password">パスワード</TabsTrigger>
            </TabsList>
            <TabsContent value="account">
              <Card>
                <CardHeader>
                  <CardTitle>アカウント</CardTitle>
                  <CardDescription>
                    アカウント情報を変更します。
                    <br />
                    完了したら保存をクリックしてください。
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
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="email">メールアドレス</Label>
                    <Input
                      id="email"
                      value={formData.email}
                      onChange={e => handleInputChange("email", e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="password">
              <Card>
                <CardHeader>
                  <CardTitle>パスワード</CardTitle>
                  <CardDescription>
                    パスワードを変更します。
                    <br />
                    完了したら保存をクリックしてください。
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6">
                  <div className="grid gap-3">
                    <Label htmlFor="current">現在のパスワード</Label>
                    <Input
                      id="current"
                      type="password"
                      value={passwordData.current_password}
                      onChange={e =>
                        handlePasswordChange("current_password", e.target.value)
                      }
                      disabled={isLoading}
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="new">新しいパスワード</Label>
                    <Input
                      id="new"
                      type="password"
                      value={passwordData.new_password}
                      onChange={e =>
                        handlePasswordChange("new_password", e.target.value)
                      }
                      disabled={isLoading}
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="confirm">新しいパスワード（確認）</Label>
                    <Input
                      id="confirm"
                      type="password"
                      value={passwordData.confirm_password}
                      onChange={e =>
                        handlePasswordChange("confirm_password", e.target.value)
                      }
                      disabled={isLoading}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
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

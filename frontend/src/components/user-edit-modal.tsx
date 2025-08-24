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

  // ユーザーデータが変更されたときにフォームを更新
  React.useEffect(() => {
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
      });
    }
  }, [user]);

  const handleSave = () => {
    if (user && onSave) {
      onSave({
        ...user,
        ...formData,
      });
    }
    onClose();
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({
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
                      onChange={(e) =>
                        handleInputChange("name", e.target.value)
                      }
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="email">メールアドレス</Label>
                    <Input
                      id="email"
                      value={formData.email}
                      onChange={(e) =>
                        handleInputChange("email", e.target.value)
                      }
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
                    <Input id="current" type="password" />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="new">新しいパスワード</Label>
                    <Input id="new" type="password" />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="confirm">新しいパスワード（確認）</Label>
                    <Input id="confirm" type="password" />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            キャンセル
          </Button>
          <Button onClick={handleSave}>保存</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

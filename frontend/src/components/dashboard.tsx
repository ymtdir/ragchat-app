import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";

export function Dashboard() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">ダッシュボード</h1>
          <Button onClick={logout} variant="outline">
            ログアウト
          </Button>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>ようこそ</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                ダッシュボードへようこそ！ここにアプリケーションの機能を追加できます。
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>機能予定</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>ドキュメント管理</li>
                <li>チャット機能</li>
                <li>設定画面</li>
                <li>ユーザープロフィール</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

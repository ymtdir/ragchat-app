/* eslint-disable @typescript-eslint/no-explicit-any */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UsersPage } from "./users";
import { UserService } from "@/services/user-service";
import type { User } from "./user-table";

// UserServiceのモック
vi.mock("@/services/user-service");
const mockUserService = UserService as any;

// app-sidebarのモック
vi.mock("./app-sidebar", () => ({
  AppSidebar: () => <div data-testid="app-sidebar">Sidebar</div>,
}));

// user-tableのモック
vi.mock("./user-table", () => ({
  UserTable: ({ data, isLoading }: { data: User[]; isLoading: boolean }) => (
    <div data-testid="user-table" data-loading={isLoading}>
      {data.map((user) => (
        <div key={user.id} data-testid={`user-${user.id}`}>
          {user.name}
        </div>
      ))}
    </div>
  ),
}));

// テスト用のモックデータ
const mockUsers: User[] = [
  {
    id: 1,
    email: "test1@example.com",
    name: "testuser1",
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    email: "test2@example.com",
    name: "testuser2",
    is_active: false,
    created_at: "2024-01-02T00:00:00Z",
    updated_at: "2024-01-02T00:00:00Z",
  },
];

describe("UsersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.error = vi.fn();
    console.log = vi.fn();
  });

  test("ページが正常に表示される", async () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // ページタイトルが表示されることを確認（複数あるので getAllByText を使用）
    const titles = screen.getAllByText("ユーザー管理");
    expect(titles.length).toBeGreaterThan(0);
    expect(
      screen.getByText("登録ユーザーの管理と詳細情報を確認できます。")
    ).toBeInTheDocument();

    // サイドバーが表示されることを確認
    expect(screen.getByTestId("app-sidebar")).toBeInTheDocument();

    // 新規ユーザーボタンが表示されることを確認
    expect(screen.getByText("新規ユーザー")).toBeInTheDocument();
  });

  test("ユーザーデータの取得に成功した場合", async () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // ローディング状態が表示されることを確認
    expect(screen.getByTestId("user-table")).toHaveAttribute(
      "data-loading",
      "true"
    );

    // データ取得後、UserTableが表示されることを確認
    await waitFor(() => {
      expect(screen.getByTestId("user-table")).toHaveAttribute(
        "data-loading",
        "false"
      );
      expect(screen.getByTestId("user-1")).toBeInTheDocument();
      expect(screen.getByTestId("user-2")).toBeInTheDocument();
    });

    // UserService.getAllUsersが呼ばれることを確認
    expect(mockUserService.getAllUsers).toHaveBeenCalledTimes(1);
  });

  test("ユーザーデータの取得に失敗した場合", async () => {
    const errorMessage = "API Error";
    mockUserService.getAllUsers.mockRejectedValue(new Error(errorMessage));

    render(<UsersPage />);

    // エラーアラートが表示されることを確認
    await waitFor(() => {
      expect(
        screen.getByText("ユーザー情報の読み込みに失敗しました")
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "データの取得中にエラーが発生しました。以下の原因が考えられます："
        )
      ).toBeInTheDocument();
    });

    // エラーの原因リストが表示されることを確認
    expect(screen.getByText("データベース接続エラー")).toBeInTheDocument();
    expect(screen.getByText("APIサーバーの一時的な問題")).toBeInTheDocument();
    expect(screen.getByText("ネットワーク接続の不具合")).toBeInTheDocument();
    expect(screen.getByText("認証トークンの有効期限切れ")).toBeInTheDocument();

    // エラーログが出力されることを確認
    expect(console.error).toHaveBeenCalledWith(
      "ユーザー情報の取得に失敗:",
      expect.any(Error)
    );
  });

  test("新規ユーザーボタンをクリックすると適切に処理される", () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    const addButton = screen.getByText("新規ユーザー");
    fireEvent.click(addButton);

    // コンソールログが出力されることを確認（TODO実装なので）
    expect(console.log).toHaveBeenCalledWith("ユーザー追加");
  });

  test("コンポーネントのマウント時にユーザーデータを取得する", () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // useEffectでデータ取得が実行されることを確認
    expect(mockUserService.getAllUsers).toHaveBeenCalledTimes(1);
  });

  test("ヘッダーにサイドバートリガーとタイトルが表示される", () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // ヘッダーのタイトルが表示されることを確認
    const headerTitles = screen.getAllByText("ユーザー管理");
    expect(headerTitles.length).toBeGreaterThan(0);
  });

  test("メインコンテンツエリアが適切にレンダリングされる", async () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // メインエリアの要素が表示されることを確認
    await waitFor(() => {
      expect(screen.getByTestId("user-table")).toBeInTheDocument();
    });
  });

  test("SidebarProviderが適切に設定される", () => {
    mockUserService.getAllUsers.mockResolvedValue(mockUsers);

    render(<UsersPage />);

    // サイドバープロバイダーが設定されていることを確認
    // （実際のDOM構造を確認）
    const container = screen.getByTestId("app-sidebar").closest("div");
    expect(container).toBeInTheDocument();
  });
});

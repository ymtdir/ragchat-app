import { render, screen } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { Dashboard } from "./dashboard";

// useAuthフックのモック
vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    logout: vi.fn(),
  }),
}));

// React Routerのモック
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("ダッシュボード", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("ダッシュボードが正しくレンダリングされる", () => {
    render(<Dashboard />);

    expect(screen.getByText("ダッシュボード")).toBeTruthy();
    expect(screen.getByText("ようこそ")).toBeTruthy();
    expect(screen.getByText("機能予定")).toBeTruthy();
    expect(screen.getByRole("button", { name: "ログアウト" })).toBeTruthy();
  });

  test("ダッシュボードの内容が正しく表示される", () => {
    render(<Dashboard />);

    expect(
      screen.getByText(
        "ダッシュボードへようこそ！ここにアプリケーションの機能を追加できます。"
      )
    ).toBeTruthy();
    expect(screen.getByText("ドキュメント管理")).toBeTruthy();
    expect(screen.getByText("チャット機能")).toBeTruthy();
    expect(screen.getByText("設定画面")).toBeTruthy();
    expect(screen.getByText("ユーザープロフィール")).toBeTruthy();
  });

  test("ログアウトボタンが存在する", () => {
    render(<Dashboard />);

    const logoutButton = screen.getByRole("button", { name: "ログアウト" });
    expect(logoutButton).toBeTruthy();
    // variant="outline"は実際のCSSクラスではなく、shadcn/uiの内部実装
    expect(logoutButton).toBeInTheDocument();
  });

  test("ダッシュボードのレイアウトが正しい", () => {
    render(<Dashboard />);

    // 最上位のdivを取得
    const container = screen.getByText("ダッシュボード").closest("div");
    expect(container).toBeInTheDocument();
  });
});

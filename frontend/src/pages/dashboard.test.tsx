import { render, screen } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { Dashboard } from "./dashboard";

// SidebarProviderとSidebarTriggerのモック
vi.mock("@/components/ui/sidebar", () => ({
  SidebarProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-provider">{children}</div>
  ),
  SidebarTrigger: () => <button data-testid="sidebar-trigger">Menu</button>,
}));

// AppSidebarのモック
vi.mock("@/components/layout/app-sidebar", () => ({
  AppSidebar: () => <div data-testid="app-sidebar">Sidebar</div>,
}));

describe("ダッシュボード", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("ダッシュボードが正しくレンダリングされる", () => {
    render(<Dashboard />);

    expect(screen.getByText("ダッシュボード")).toBeTruthy();
    expect(screen.getByText("ダッシュボードの内容")).toBeTruthy();
    expect(screen.getByTestId("sidebar-provider")).toBeTruthy();
    expect(screen.getByTestId("app-sidebar")).toBeTruthy();
    expect(screen.getByTestId("sidebar-trigger")).toBeTruthy();
  });

  test("サイドバーが統合されている", () => {
    render(<Dashboard />);

    expect(screen.getByTestId("app-sidebar")).toBeTruthy();
    expect(screen.getByTestId("sidebar-trigger")).toBeTruthy();
  });

  test("ヘッダーが正しく表示される", () => {
    render(<Dashboard />);

    expect(screen.getByText("ダッシュボード")).toBeTruthy();
  });

  test("メインコンテンツが表示される", () => {
    render(<Dashboard />);

    expect(screen.getByText("ダッシュボードの内容")).toBeTruthy();
  });
});

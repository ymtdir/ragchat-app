import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AppSidebar } from "./app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";

// useAuthフックのモック
const mockLogout = vi.fn();
vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    logout: mockLogout,
  }),
}));

// SidebarProviderのモック
vi.mock("@/components/ui/sidebar", () => ({
  SidebarProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-provider">{children}</div>
  ),
  Sidebar: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar">{children}</div>
  ),
  SidebarContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-content">{children}</div>
  ),
  SidebarGroup: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-group">{children}</div>
  ),
  SidebarGroupLabel: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-group-label">{children}</div>
  ),
  SidebarGroupContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-group-content">{children}</div>
  ),
  SidebarMenu: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-menu">{children}</div>
  ),
  SidebarMenuItem: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-menu-item">{children}</div>
  ),
  SidebarMenuButton: ({
    children,
    onClick,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
  }) => (
    <button data-testid="sidebar-menu-button" onClick={onClick}>
      {children}
    </button>
  ),
  SidebarFooter: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="sidebar-footer">{children}</div>
  ),
}));

// テスト用のラッパー関数
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <SidebarProvider>{component}</SidebarProvider>
    </MemoryRouter>
  );
};

describe("AppSidebar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("サイドバーが正しくレンダリングされる", () => {
    renderWithRouter(<AppSidebar />);

    expect(screen.getByText("RagChat App")).toBeTruthy();
    expect(screen.getByText("Dashboard")).toBeTruthy();
    expect(screen.getByText("Users")).toBeTruthy();
    expect(screen.getByText("Documents")).toBeTruthy();
    expect(screen.getByText("Settings")).toBeTruthy();
    expect(screen.getByText("Logout")).toBeTruthy();
  });

  test("ログアウトボタンがクリック可能", async () => {
    renderWithRouter(<AppSidebar />);

    const logoutButton = screen.getByText("Logout");
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });

  test("メニューアイテムが正しく表示される", () => {
    renderWithRouter(<AppSidebar />);

    expect(screen.getByText("Dashboard")).toBeTruthy();
    expect(screen.getByText("Users")).toBeTruthy();
    expect(screen.getByText("Documents")).toBeTruthy();
    expect(screen.getByText("Settings")).toBeTruthy();
  });

  test("メニューアイテムのリンクが正しい", () => {
    renderWithRouter(<AppSidebar />);

    const dashboardLink = screen.getByText("Dashboard").closest("a");
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");

    const usersLink = screen.getByText("Users").closest("a");
    expect(usersLink).toHaveAttribute("href", "/users");

    const documentsLink = screen.getByText("Documents").closest("a");
    expect(documentsLink).toHaveAttribute("href", "/");

    const settingsLink = screen.getByText("Settings").closest("a");
    expect(settingsLink).toHaveAttribute("href", "/");
  });

  test("サイドバーの構造が正しい", () => {
    renderWithRouter(<AppSidebar />);

    expect(screen.getByTestId("sidebar")).toBeTruthy();
    expect(screen.getByTestId("sidebar-content")).toBeTruthy();
    expect(screen.getByTestId("sidebar-footer")).toBeTruthy();
  });
});

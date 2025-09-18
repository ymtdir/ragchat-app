// モック定義
vi.mock("@/utils/auth-loader", () => ({
  guestRoute: vi.fn(),
  protectedRoute: vi.fn(),
}));

vi.mock("@/pages/signin-form", () => ({
  SignInForm: () => <div data-testid="signin-form">SignInForm</div>,
}));

vi.mock("@/pages/signup-form", () => ({
  SignUpForm: () => <div data-testid="signup-form">SignUpForm</div>,
}));

vi.mock("@/pages/dashboard", () => ({
  Dashboard: () => <div data-testid="dashboard">Dashboard</div>,
}));

vi.mock("@/pages/users", () => ({
  UsersPage: () => <div data-testid="users-page">UsersPage</div>,
}));

vi.mock("@/pages/groups", () => ({
  GroupsPage: () => <div data-testid="groups-page">GroupsPage</div>,
}));

import { expect, test, describe, vi, beforeEach } from "vitest";
import { createGuestRoutes, createProtectedRoutes } from "./index";
import { guestRoute, protectedRoute } from "@/utils/auth-loader";

describe("routes", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("createGuestRoutes", () => {
    test("正しい数のゲストルートを作成する", () => {
      const routes = createGuestRoutes();

      expect(routes).toHaveLength(3);
      expect(guestRoute).toHaveBeenCalledTimes(3);
    });

    test("正しいパスでゲストルートを作成する", () => {
      createGuestRoutes();

      expect(guestRoute).toHaveBeenCalledWith("/", expect.anything());
      expect(guestRoute).toHaveBeenCalledWith("/signin", expect.anything());
      expect(guestRoute).toHaveBeenCalledWith("/signup", expect.anything());
    });
  });

  describe("createProtectedRoutes", () => {
    test("正しい数の保護されたルートを作成する", () => {
      const routes = createProtectedRoutes();

      expect(routes).toHaveLength(3);
      expect(protectedRoute).toHaveBeenCalledTimes(3);
    });

    test("正しいパスで保護されたルートを作成する", () => {
      createProtectedRoutes();

      expect(protectedRoute).toHaveBeenCalledWith(
        "/dashboard",
        expect.anything()
      );
      expect(protectedRoute).toHaveBeenCalledWith("/users", expect.anything());
      expect(protectedRoute).toHaveBeenCalledWith("/groups", expect.anything());
    });
  });
});

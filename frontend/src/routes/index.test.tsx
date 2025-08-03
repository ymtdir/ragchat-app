// モック定義
vi.mock("@/utils/auth-loader", () => ({
  guestRoute: vi.fn(),
  protectedRoute: vi.fn(),
}));

vi.mock("@/components/signin-form", () => ({
  SignInForm: () => <div data-testid="signin-form">SignInForm</div>,
}));

vi.mock("@/components/signup-form", () => ({
  SignUpForm: () => <div data-testid="signup-form">SignUpForm</div>,
}));

vi.mock("@/components/dashboard", () => ({
  Dashboard: () => <div data-testid="dashboard">Dashboard</div>,
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

      expect(routes).toHaveLength(1);
      expect(protectedRoute).toHaveBeenCalledTimes(1);
    });

    test("正しいパスで保護されたルートを作成する", () => {
      createProtectedRoutes();

      expect(protectedRoute).toHaveBeenCalledWith(
        "/dashboard",
        expect.anything()
      );
    });
  });
});

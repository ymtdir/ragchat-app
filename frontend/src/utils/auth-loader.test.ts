import { expect, test, describe, vi, beforeEach } from "vitest";
import { requireAuth, requireGuest } from "./auth-loader";

// React Routerのモック
vi.mock("react-router-dom", () => ({
  redirect: vi.fn(() => {
    throw new Error("redirect");
  }),
}));

describe("auth-loader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe("requireAuth", () => {
    test("トークンがある場合はトークンを返す", () => {
      localStorage.setItem("access_token", "test-token");

      const result = requireAuth();

      expect(result).toEqual({ token: "test-token" });
    });

    test("トークンがない場合はリダイレクトする", () => {
      expect(() => requireAuth()).toThrow("redirect");
    });
  });

  describe("requireGuest", () => {
    test("トークンがない場合はnullを返す", () => {
      const result = requireGuest();

      expect(result).toBeNull();
    });

    test("トークンがある場合はリダイレクトする", () => {
      localStorage.setItem("access_token", "test-token");

      expect(() => requireGuest()).toThrow("redirect");
    });
  });
});

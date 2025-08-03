import { renderHook, act } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { useAuth } from "./use-auth";

// React Routerのモック
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  test("logout関数が正しく動作する", () => {
    // トークンを設定
    localStorage.setItem("access_token", "test-token");

    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.logout();
    });

    // localStorageからトークンが削除されることを確認
    expect(localStorage.getItem("access_token")).toBeNull();

    // navigateが正しく呼ばれることを確認
    expect(mockNavigate).toHaveBeenCalledWith("/signin");
  });

  test("logout関数が存在する", () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.logout).toBeDefined();
    expect(typeof result.current.logout).toBe("function");
  });
});

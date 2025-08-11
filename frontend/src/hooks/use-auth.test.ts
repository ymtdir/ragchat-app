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

// fetchのモック
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  test("logout関数が正しく動作する", async () => {
    // トークンを設定
    localStorage.setItem("access_token", "test-token");

    // fetchのモックレスポンス
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
    });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.logout();
    });

    // APIが呼ばれることを確認
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/auth/logout",
      expect.objectContaining({
        method: "POST",
        headers: {
          Authorization: "Bearer test-token",
          "Content-Type": "application/json",
        },
      })
    );

    // localStorageからトークンが削除されることを確認
    expect(localStorage.getItem("access_token")).toBeNull();

    // navigateが正しく呼ばれることを確認
    expect(mockNavigate).toHaveBeenCalledWith("/signin");
  });

  test("logout関数がAPIエラーでもローカルストレージを削除する", async () => {
    // トークンを設定
    localStorage.setItem("access_token", "test-token");

    // fetchのモックレスポンス（エラー）
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.logout();
    });

    // APIが呼ばれることを確認
    expect(fetch).toHaveBeenCalled();

    // エラーが発生してもローカルストレージからトークンが削除されることを確認
    expect(localStorage.getItem("access_token")).toBeNull();

    // navigateが正しく呼ばれることを確認
    expect(mockNavigate).toHaveBeenCalledWith("/signin");
  });

  test("logout関数がネットワークエラーでもローカルストレージを削除する", async () => {
    // トークンを設定
    localStorage.setItem("access_token", "test-token");

    // fetchのモックレスポンス（ネットワークエラー）
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.logout();
    });

    // APIが呼ばれることを確認
    expect(fetch).toHaveBeenCalled();

    // エラーが発生してもローカルストレージからトークンが削除されることを確認
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

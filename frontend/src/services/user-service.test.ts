import { expect, test, describe, vi, beforeEach, afterEach } from "vitest";
import { UserService } from "./user-service";
import type { User } from "@/types/api";

// fetchのモック
const mockFetch = vi.fn();
global.fetch = mockFetch;

// localStorageのモック
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, "localStorage", {
  value: mockLocalStorage,
});

// テスト用のモックデータ
const mockUsers: User[] = [
  {
    id: 1,
    email: "test1@example.com",
    name: "testuser1",
  },
  {
    id: 2,
    email: "test2@example.com",
    name: "testuser2",
  },
];

const mockUser: User = mockUsers[0];

describe("UserService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.error = vi.fn();
    mockLocalStorage.getItem.mockReturnValue("mock-token");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getAllUsers", () => {
    test("成功時にユーザーリストを返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ users: mockUsers }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await UserService.getAllUsers();

      expect(result).toEqual(mockUsers);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("レスポンスにusersプロパティがない場合は空配列を返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await UserService.getAllUsers();

      expect(result).toEqual([]);
    });

    test("HTTPエラーの場合は例外をスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn(),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(UserService.getAllUsers()).rejects.toThrow(
        "HTTP error! status: 500"
      );

      expect(console.error).toHaveBeenCalledWith(
        "ユーザー取得エラー:",
        expect.any(Error)
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(UserService.getAllUsers()).rejects.toThrow("Network error");

      expect(console.error).toHaveBeenCalledWith(
        "ユーザー取得エラー:",
        networkError
      );
    });

    test("トークンがない場合でもAPIを呼び出す", async () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ users: mockUsers }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await UserService.getAllUsers();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer null",
            "Content-Type": "application/json",
          },
        }
      );
    });
  });

  describe("getUserById", () => {
    test("成功時に特定のユーザーを返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockUser),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await UserService.getUserById(1);

      expect(result).toEqual(mockUser);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/1",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("HTTPエラーの場合は例外をスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        json: vi.fn(),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(UserService.getUserById(999)).rejects.toThrow(
        "HTTP error! status: 404"
      );

      expect(console.error).toHaveBeenCalledWith(
        "ユーザー取得エラー:",
        expect.any(Error)
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(UserService.getUserById(1)).rejects.toThrow("Network error");

      expect(console.error).toHaveBeenCalledWith(
        "ユーザー取得エラー:",
        networkError
      );
    });

    test("異なるユーザーIDでAPIを呼び出す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockUser),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await UserService.getUserById(123);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/123",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
    });

    test("トークンがない場合でもAPIを呼び出す", async () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockUser),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await UserService.getUserById(1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/1",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer null",
            "Content-Type": "application/json",
          },
        }
      );
    });
  });

  describe("環境変数", () => {
    test("デフォルト値が正しく使用される", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ users: mockUsers }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await UserService.getAllUsers();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
    });
  });
});

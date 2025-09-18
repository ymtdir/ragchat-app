import { expect, test, describe, vi, beforeEach, afterEach } from "vitest";
import { GroupService } from "./group-service";
import type { Group, GroupCreate, GroupUpdate } from "@/types/api";

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
const mockGroups: Group[] = [
  {
    id: 1,
    name: "開発チーム",
    description: "Webアプリケーション開発チーム",
    created_at: "2024-01-01T10:00:00Z",
    updated_at: "2024-01-01T10:00:00Z",
    deleted_at: null,
  },
  {
    id: 2,
    name: "デザインチーム",
    description: "UI/UXデザインチーム",
    created_at: "2024-01-02T10:00:00Z",
    updated_at: "2024-01-02T10:00:00Z",
    deleted_at: null,
  },
];

const mockGroup: Group = mockGroups[0];

const mockGroupCreate: GroupCreate = {
  name: "新規グループ",
  description: "新規グループの説明",
};

const mockGroupUpdate: GroupUpdate = {
  name: "更新されたグループ",
  description: "更新されたグループの説明",
};

describe("GroupService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.error = vi.fn();
    mockLocalStorage.getItem.mockReturnValue("mock-token");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getAllGroups", () => {
    test("成功時にグループリストを返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ groups: mockGroups }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await GroupService.getAllGroups();

      expect(result).toEqual(mockGroups);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/",
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

    test("レスポンスにgroupsプロパティがない場合は空配列を返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await GroupService.getAllGroups();

      expect(result).toEqual([]);
    });

    test("HTTPエラーの場合は例外をスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn(),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.getAllGroups()).rejects.toThrow(
        "HTTP error! status: 500"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ取得エラー:",
        expect.any(Error)
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(GroupService.getAllGroups()).rejects.toThrow(
        "Network error"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ取得エラー:",
        networkError
      );
    });

    test("トークンがない場合でもAPIを呼び出す", async () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ groups: mockGroups }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await GroupService.getAllGroups();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/",
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

  describe("getGroupById", () => {
    test("成功時に特定のグループを返す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockGroup),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await GroupService.getGroupById(1);

      expect(result).toEqual(mockGroup);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/1",
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

      await expect(GroupService.getGroupById(999)).rejects.toThrow(
        "HTTP error! status: 404"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ取得エラー:",
        expect.any(Error)
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(GroupService.getGroupById(1)).rejects.toThrow(
        "Network error"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ取得エラー:",
        networkError
      );
    });

    test("異なるグループIDでAPIを呼び出す", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockGroup),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await GroupService.getGroupById(123);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/123",
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
        json: vi.fn().mockResolvedValue(mockGroup),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await GroupService.getGroupById(1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/1",
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

  describe("createGroup", () => {
    test("成功時に作成されたグループを返す", async () => {
      const mockResponse = {
        ok: true,
        status: 201,
        json: vi.fn().mockResolvedValue(mockGroup),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await GroupService.createGroup(mockGroupCreate);

      expect(result).toEqual(mockGroup);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/",
        {
          method: "POST",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(mockGroupCreate),
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("HTTPエラーの場合は詳細なエラーメッセージをスローする", async () => {
      const errorDetail = "グループ名が既に使用されています";
      const mockResponse = {
        ok: false,
        status: 400,
        json: vi.fn().mockResolvedValue({ detail: errorDetail }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.createGroup(mockGroupCreate)).rejects.toThrow(
        errorDetail
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ作成エラー:",
        expect.any(Error)
      );
    });

    test("HTTPエラーでdetailがない場合はデフォルトメッセージをスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.createGroup(mockGroupCreate)).rejects.toThrow(
        "HTTP error! status: 500"
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(GroupService.createGroup(mockGroupCreate)).rejects.toThrow(
        "Network error"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ作成エラー:",
        networkError
      );
    });
  });

  describe("updateGroup", () => {
    test("成功時に更新されたグループを返す", async () => {
      const updatedGroup = { ...mockGroup, ...mockGroupUpdate };
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(updatedGroup),
      };
      mockFetch.mockResolvedValue(mockResponse);

      const result = await GroupService.updateGroup(1, mockGroupUpdate);

      expect(result).toEqual(updatedGroup);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/1",
        {
          method: "PUT",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(mockGroupUpdate),
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("HTTPエラーの場合は詳細なエラーメッセージをスローする", async () => {
      const errorDetail = "グループが見つかりません";
      const mockResponse = {
        ok: false,
        status: 404,
        json: vi.fn().mockResolvedValue({ detail: errorDetail }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(
        GroupService.updateGroup(999, mockGroupUpdate)
      ).rejects.toThrow(errorDetail);

      expect(console.error).toHaveBeenCalledWith(
        "グループ更新エラー:",
        expect.any(Error)
      );
    });

    test("HTTPエラーでdetailがない場合はデフォルトメッセージをスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(
        GroupService.updateGroup(1, mockGroupUpdate)
      ).rejects.toThrow("HTTP error! status: 500");
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(
        GroupService.updateGroup(1, mockGroupUpdate)
      ).rejects.toThrow("Network error");

      expect(console.error).toHaveBeenCalledWith(
        "グループ更新エラー:",
        networkError
      );
    });
  });

  describe("deleteGroup", () => {
    test("成功時に正常に完了する", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ message: "削除成功" }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteGroup(1)).resolves.toBeUndefined();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/1",
        {
          method: "DELETE",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("HTTPエラーの場合は詳細なエラーメッセージをスローする", async () => {
      const errorDetail = "グループが見つかりません";
      const mockResponse = {
        ok: false,
        status: 404,
        json: vi.fn().mockResolvedValue({ detail: errorDetail }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteGroup(999)).rejects.toThrow(errorDetail);

      expect(console.error).toHaveBeenCalledWith(
        "グループ削除エラー:",
        expect.any(Error)
      );
    });

    test("HTTPエラーでdetailがない場合はデフォルトメッセージをスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteGroup(1)).rejects.toThrow(
        "HTTP error! status: 500"
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(GroupService.deleteGroup(1)).rejects.toThrow(
        "Network error"
      );

      expect(console.error).toHaveBeenCalledWith(
        "グループ削除エラー:",
        networkError
      );
    });
  });

  describe("deleteAllGroups", () => {
    test("成功時に正常に完了する", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ message: "全削除成功" }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteAllGroups()).resolves.toBeUndefined();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/",
        {
          method: "DELETE",
          headers: {
            Authorization: "Bearer mock-token",
            "Content-Type": "application/json",
          },
        }
      );
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
    });

    test("HTTPエラーの場合は詳細なエラーメッセージをスローする", async () => {
      const errorDetail = "権限が不足しています";
      const mockResponse = {
        ok: false,
        status: 403,
        json: vi.fn().mockResolvedValue({ detail: errorDetail }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteAllGroups()).rejects.toThrow(errorDetail);

      expect(console.error).toHaveBeenCalledWith(
        "全グループ削除エラー:",
        expect.any(Error)
      );
    });

    test("HTTPエラーでdetailがない場合はデフォルトメッセージをスローする", async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({}),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await expect(GroupService.deleteAllGroups()).rejects.toThrow(
        "HTTP error! status: 500"
      );
    });

    test("ネットワークエラーの場合は例外をスローする", async () => {
      const networkError = new Error("Network error");
      mockFetch.mockRejectedValue(networkError);

      await expect(GroupService.deleteAllGroups()).rejects.toThrow(
        "Network error"
      );

      expect(console.error).toHaveBeenCalledWith(
        "全グループ削除エラー:",
        networkError
      );
    });
  });

  describe("環境変数", () => {
    test("デフォルト値が正しく使用される", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({ groups: mockGroups }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      await GroupService.getAllGroups();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/",
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

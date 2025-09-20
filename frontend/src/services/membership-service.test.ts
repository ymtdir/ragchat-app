import { expect, test, describe, vi, beforeEach, afterEach } from "vitest";
import { MembershipService } from "./membership-service";
import type {
  MembersResponse,
  UserMembershipsResponse,
  MembershipCreate,
  Membership,
  BulkMembershipCreate,
  BulkMembershipResponse,
  BulkMembershipDelete,
  BulkMembershipDeleteResponse,
  MemberDeleteResponse,
  User,
  Member,
} from "@/types/api";

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

// console.logとconsole.errorのモック
let mockConsoleLog: ReturnType<typeof vi.spyOn>;

// テスト用のモックデータ
const mockMembers: Member[] = [
  {
    membership_id: 1,
    user_id: 1,
    user_name: "田中太郎",
    user_email: "tanaka@example.com",
    joined_at: "2024-01-01T10:00:00Z",
    is_active: true,
  },
  {
    membership_id: 2,
    user_id: 2,
    user_name: "佐藤花子",
    user_email: "sato@example.com",
    joined_at: "2024-01-02T10:00:00Z",
    is_active: true,
  },
];

const mockMembersResponse: MembersResponse = {
  group_id: 1,
  members: mockMembers,
  total_count: 2,
};

const mockUsers: User[] = [
  {
    id: 3,
    name: "山田次郎",
    email: "yamada@example.com",
    created_at: "2024-01-03T10:00:00Z",
    updated_at: "2024-01-03T10:00:00Z",
    deleted_at: null,
  },
  {
    id: 4,
    name: "鈴木三郎",
    email: "suzuki@example.com",
    created_at: "2024-01-04T10:00:00Z",
    updated_at: "2024-01-04T10:00:00Z",
    deleted_at: null,
  },
];

const mockUserMembershipsResponse: UserMembershipsResponse = {
  user_id: 1,
  memberships: [
    {
      membership_id: 1,
      group_id: 1,
      group_name: "開発チーム",
      group_description: "Webアプリケーション開発チーム",
      joined_at: "2024-01-01T10:00:00Z",
      is_active: true,
    },
  ],
  total_count: 1,
};

const mockMembership: Membership = {
  id: 3,
  user_id: 3,
  group_id: 1,
  created_at: "2024-01-05T10:00:00Z",
  updated_at: "2024-01-05T10:00:00Z",
  deleted_at: null,
  is_active: true,
};

const mockMembershipCreate: MembershipCreate = {
  user_id: 3,
  group_id: 1,
};

const mockBulkMembershipCreate: BulkMembershipCreate = {
  group_id: 1,
  user_ids: [3, 4],
};

const mockBulkMembershipResponse: BulkMembershipResponse = {
  added_count: 2,
  already_member_count: 0,
  errors: [],
};

const mockBulkMembershipDelete: BulkMembershipDelete = {
  group_id: 1,
  user_ids: [1, 2],
};

const mockBulkMembershipDeleteResponse: BulkMembershipDeleteResponse = {
  removed_count: 2,
  not_member_count: 0,
  errors: [],
};

const mockMemberDeleteResponse: MemberDeleteResponse = {
  message: "メンバーが正常に削除されました",
};

describe("MembershipService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue("test-token");
    // 各テストの前にコンソールモックを設定
    mockConsoleLog = vi.spyOn(console, "log").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("認証関連", () => {
    test("認証トークンが存在しない場合はエラーを投げる", async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      await expect(MembershipService.getGroupMembers(1)).rejects.toThrow(
        "認証トークンが見つかりません。ログインしてください。"
      );
    });

    test("認証ヘッダーが正しく設定される", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      await MembershipService.getGroupMembers(1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/members?include_deleted=false",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
        }
      );
    });
  });

  describe("getGroupMembers", () => {
    test("グループのメンバー一覧を正常に取得できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      const result = await MembershipService.getGroupMembers(1);

      expect(result).toEqual(mockMembersResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/members?include_deleted=false",
        expect.objectContaining({
          method: "GET",
        })
      );
    });

    test("削除されたメンバーも含める場合のパラメータが正しく設定される", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      await MembershipService.getGroupMembers(1, true);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/members?include_deleted=true",
        expect.objectContaining({
          method: "GET",
        })
      );
    });

    test("APIエラー時にエラーメッセージを投げる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
        url: "http://localhost:8000/api/memberships/groups/999/members",
        text: async () =>
          JSON.stringify({ detail: "グループが見つかりません" }),
      });

      await expect(MembershipService.getGroupMembers(999)).rejects.toThrow(
        "グループが見つかりません"
      );
    });
  });

  describe("getUserMemberships", () => {
    test("ユーザーの所属グループ一覧を正常に取得できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/users/1/groups",
        json: async () => mockUserMembershipsResponse,
      });

      const result = await MembershipService.getUserMemberships(1);

      expect(result).toEqual(mockUserMembershipsResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/users/1/groups?include_deleted=false",
        expect.objectContaining({
          method: "GET",
        })
      );
    });

    test("削除されたメンバーシップも含める場合のパラメータが正しく設定される", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/users/1/groups",
        json: async () => mockUserMembershipsResponse,
      });

      await MembershipService.getUserMemberships(1, true);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/users/1/groups?include_deleted=true",
        expect.objectContaining({
          method: "GET",
        })
      );
    });
  });

  describe("addMemberToGroup", () => {
    test("グループにメンバーを正常に追加できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        statusText: "Created",
        url: "http://localhost:8000/api/memberships/",
        json: async () => mockMembership,
      });

      const result =
        await MembershipService.addMemberToGroup(mockMembershipCreate);

      expect(result).toEqual(mockMembership);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
          body: JSON.stringify(mockMembershipCreate),
        }
      );
    });

    test("既存メンバーの場合はエラーを投げる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        url: "http://localhost:8000/api/memberships/",
        text: async () =>
          JSON.stringify({
            detail: "ユーザーは既にこのグループのメンバーです",
          }),
      });

      await expect(
        MembershipService.addMemberToGroup(mockMembershipCreate)
      ).rejects.toThrow("ユーザーは既にこのグループのメンバーです");
    });
  });

  describe("removeMemberFromGroup", () => {
    test("グループからメンバーを正常に削除できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/users/1",
        json: async () => mockMemberDeleteResponse,
      });

      const result = await MembershipService.removeMemberFromGroup(1, 1);

      expect(result).toEqual(mockMemberDeleteResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/users/1",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
        }
      );
    });

    test("存在しないメンバーの場合はエラーを投げる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
        url: "http://localhost:8000/api/memberships/groups/1/users/999",
        text: async () =>
          JSON.stringify({
            detail: "指定されたメンバーシップが見つかりません",
          }),
      });

      await expect(
        MembershipService.removeMemberFromGroup(1, 999)
      ).rejects.toThrow("指定されたメンバーシップが見つかりません");
    });
  });

  describe("addMultipleMembersToGroup", () => {
    test("複数のメンバーを一括追加できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/bulk-add",
        json: async () => mockBulkMembershipResponse,
      });

      const result = await MembershipService.addMultipleMembersToGroup(
        mockBulkMembershipCreate
      );

      expect(result).toEqual(mockBulkMembershipResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/bulk-add",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
          body: JSON.stringify(mockBulkMembershipCreate),
        }
      );
    });

    test("一部追加失敗時にもレスポンスを返す", async () => {
      const partialSuccessResponse: BulkMembershipResponse = {
        added_count: 1,
        already_member_count: 1,
        errors: ["ユーザー 4 は既にメンバーです"],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/bulk-add",
        json: async () => partialSuccessResponse,
      });

      const result = await MembershipService.addMultipleMembersToGroup(
        mockBulkMembershipCreate
      );

      expect(result).toEqual(partialSuccessResponse);
      expect(result.added_count).toBe(1);
      expect(result.already_member_count).toBe(1);
      expect(result.errors).toHaveLength(1);
    });
  });

  describe("removeMultipleMembersFromGroup", () => {
    test("複数のメンバーを一括削除できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/bulk-remove",
        json: async () => mockBulkMembershipDeleteResponse,
      });

      const result = await MembershipService.removeMultipleMembersFromGroup(
        mockBulkMembershipDelete
      );

      expect(result).toEqual(mockBulkMembershipDeleteResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/bulk-remove",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
          body: JSON.stringify(mockBulkMembershipDelete),
        }
      );
    });

    test("一部削除失敗時にもレスポンスを返す", async () => {
      const partialSuccessResponse: BulkMembershipDeleteResponse = {
        removed_count: 1,
        not_member_count: 1,
        errors: ["ユーザー 2 はメンバーではありません"],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/bulk-remove",
        json: async () => partialSuccessResponse,
      });

      const result = await MembershipService.removeMultipleMembersFromGroup(
        mockBulkMembershipDelete
      );

      expect(result).toEqual(partialSuccessResponse);
      expect(result.removed_count).toBe(1);
      expect(result.not_member_count).toBe(1);
      expect(result.errors).toHaveLength(1);
    });
  });

  describe("getAvailableUsers", () => {
    test("利用可能なユーザー一覧を正常に取得できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/users/",
        json: async () => ({ users: mockUsers }),
      });

      const result = await MembershipService.getAvailableUsers();

      expect(result).toEqual(mockUsers);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
        }
      );
    });

    test("ユーザーが存在しない場合は空配列を返す", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/users/",
        json: async () => ({ users: [] }),
      });

      const result = await MembershipService.getAvailableUsers();

      expect(result).toEqual([]);
    });
  });

  describe("getGroupMemberCount", () => {
    test("グループのメンバー数を正常に取得できる", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      const result = await MembershipService.getGroupMemberCount(1);

      expect(result).toBe(2);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/members?include_deleted=false",
        expect.objectContaining({
          method: "GET",
        })
      );
    });

    test("メンバーが存在しない場合は0を返す", async () => {
      const emptyResponse: MembersResponse = {
        group_id: 1,
        members: [],
        total_count: 0,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => emptyResponse,
      });

      const result = await MembershipService.getGroupMemberCount(1);

      expect(result).toBe(0);
    });
  });

  describe("エラーハンドリング", () => {
    test("JSONパースエラー時にテキストエラーメッセージを使用する", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        text: async () => "Internal Server Error",
      });

      await expect(MembershipService.getGroupMembers(1)).rejects.toThrow(
        "Internal Server Error"
      );
    });

    test("空のエラーレスポンス時にHTTPステータスエラーを使用する", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        text: async () => "",
      });

      await expect(MembershipService.getGroupMembers(1)).rejects.toThrow(
        "HTTPエラー: 500"
      );
    });

    test("ネットワークエラー時にエラーを投げる", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      await expect(MembershipService.getGroupMembers(1)).rejects.toThrow(
        "Network error"
      );
    });

    test("レスポンス処理が正常に動作する", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      const result = await MembershipService.getGroupMembers(1);

      expect(result).toEqual(mockMembersResponse);
      expect(mockConsoleLog).toHaveBeenCalled();
    });
  });

  describe("基本機能", () => {
    test("デフォルトAPI_BASE_URLが使用される", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        url: "http://localhost:8000/api/memberships/groups/1/members",
        json: async () => mockMembersResponse,
      });

      await MembershipService.getGroupMembers(1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/memberships/groups/1/members?include_deleted=false",
        expect.any(Object)
      );
    });
  });
});

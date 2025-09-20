import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupMemberManagementModal } from "./group-member-management-modal";
import { MembershipService } from "@/services/membership-service";
import type { Group, Member, User } from "@/types/api";

// MembershipServiceをモック
vi.mock("@/services/membership-service", () => ({
  MembershipService: {
    getGroupMembers: vi.fn(),
    getAvailableUsers: vi.fn(),
    addMultipleMembersToGroup: vi.fn(),
    removeMultipleMembersFromGroup: vi.fn(),
  },
}));

const mockGroup: Group = {
  id: 1,
  name: "開発チーム",
  description: "Webアプリケーション開発チーム",
  created_at: "2024-01-01T10:00:00Z",
  updated_at: "2024-01-01T10:00:00Z",
  deleted_at: null,
};

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

const mockOnClose = vi.fn();
const mockOnMembershipChange = vi.fn();

describe("GroupMemberManagementModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // デフォルトのモックレスポンス
    vi.mocked(MembershipService.getGroupMembers).mockResolvedValue({
      group_id: 1,
      members: mockMembers,
      total_count: 2,
    });

    vi.mocked(MembershipService.getAvailableUsers).mockResolvedValue(mockUsers);
  });

  describe("レンダリング", () => {
    test("モーダルが閉じている時は何も表示されない", () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={false}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      expect(screen.queryByText("メンバー管理:")).not.toBeInTheDocument();
    });

    test("モーダルが開いている時に正しく表示される", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      expect(screen.getByText("メンバー管理: 開発チーム")).toBeInTheDocument();

      // タブボタンを具体的に検索
      await waitFor(() => {
        expect(
          screen.getByRole("tab", { name: /現在のメンバー/ })
        ).toBeInTheDocument();
      });
    });

    test("groupがnullの場合は何も表示されない", () => {
      render(
        <GroupMemberManagementModal
          group={null}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      expect(screen.queryByText("メンバー管理:")).not.toBeInTheDocument();
    });
  });

  describe("データ取得", () => {
    test("モーダルが開かれた時にメンバー一覧とユーザー一覧を取得する", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(() => {
        expect(MembershipService.getGroupMembers).toHaveBeenCalledWith(1);
        expect(MembershipService.getAvailableUsers).toHaveBeenCalled();
      });
    });

    test("メンバー一覧が正しく表示される", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(() => {
        expect(screen.getByText("田中太郎")).toBeInTheDocument();
        expect(screen.getByText("tanaka@example.com")).toBeInTheDocument();
        expect(screen.getByText("佐藤花子")).toBeInTheDocument();
        expect(screen.getByText("sato@example.com")).toBeInTheDocument();
      });
    });
  });

  describe("タブ切り替え", () => {
    test("ユーザー追加タブが存在する", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(
        () => {
          expect(
            screen.getByRole("tab", { name: /ユーザーを追加/ })
          ).toBeInTheDocument();
        },
        { timeout: 3000 }
      );
    });

    test("ユーザー追加タブをクリックできる", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      // ユーザー追加タブをクリック
      const addUsersTab = await screen.findByRole("tab", {
        name: /ユーザーを追加/,
      });

      // クリックイベントが正常に実行されることを確認
      expect(() => {
        fireEvent.click(addUsersTab);
      }).not.toThrow();
    });
  });

  describe("メンバー管理機能", () => {
    test("現在のメンバータブにメンバーが表示される", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      // メンバーが表示されるまで待機
      await waitFor(() => {
        expect(screen.getByText("田中太郎")).toBeInTheDocument();
        expect(screen.getByText("tanaka@example.com")).toBeInTheDocument();
        expect(screen.getByText("佐藤花子")).toBeInTheDocument();
        expect(screen.getByText("sato@example.com")).toBeInTheDocument();
      });
    });

    test("チェックボックスが表示される", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(() => {
        const checkboxes = screen.getAllByRole("checkbox");
        expect(checkboxes.length).toBeGreaterThan(0);
      });
    });
  });

  describe("エラーハンドリング", () => {
    test("メンバー取得エラー時にエラーメッセージが表示される", async () => {
      vi.mocked(MembershipService.getGroupMembers).mockRejectedValue(
        new Error("ネットワークエラー")
      );

      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText(/メンバー一覧の取得に失敗しました/)
        ).toBeInTheDocument();
      });
    });

    test("ユーザー取得エラー時にエラーメッセージが表示される", async () => {
      vi.mocked(MembershipService.getAvailableUsers).mockRejectedValue(
        new Error("認証エラー")
      );

      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText(/ユーザー一覧の取得に失敗しました/)
        ).toBeInTheDocument();
      });
    });
  });

  describe("モーダル操作", () => {
    test("閉じるボタンでモーダルが閉じられる", async () => {
      render(
        <GroupMemberManagementModal
          group={mockGroup}
          isOpen={true}
          onClose={mockOnClose}
          onMembershipChange={mockOnMembershipChange}
        />
      );

      const closeButton = screen.getByText("閉じる");
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });
});

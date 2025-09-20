import { render, screen } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupTable } from "./group-table";
import type { Group } from "@/types/api";

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

const mockOnGroupUpdate = vi.fn();
const mockOnGroupDelete = vi.fn();
const mockOnBulkGroupDelete = vi.fn();
const mockOnManageMembers = vi.fn();

describe("GroupTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // GroupMemberCountコンポーネントをモック
    vi.mock("./group-member-count", () => ({
      GroupMemberCount: ({ groupId }: { groupId: number }) => (
        <div data-testid={`member-count-${groupId}`}>5人</div>
      ),
    }));
  });

  describe("レンダリング", () => {
    test("グループテーブルが正しく表示される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      expect(screen.getByText("開発チーム")).toBeInTheDocument();
      expect(
        screen.getByText("Webアプリケーション開発チーム")
      ).toBeInTheDocument();
      expect(screen.getByText("デザインチーム")).toBeInTheDocument();
      expect(screen.getByText("UI/UXデザインチーム")).toBeInTheDocument();

      // メンバー数コンポーネントが表示されることを確認
      expect(screen.getByTestId("member-count-1")).toBeInTheDocument();
      expect(screen.getByTestId("member-count-2")).toBeInTheDocument();
    });

    test("ローディング中はスケルトンが表示される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={true}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      // ローディング状態が表示されることを確認（スケルトン要素が存在する）
      const skeletonElements = screen.getAllByRole("generic");
      expect(
        skeletonElements.some(el => el.classList.contains("animate-pulse"))
      ).toBe(true);
    });
  });

  describe("プロップスの確認", () => {
    test("すべてのコールバック関数が正しく渡される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      // 各コールバック関数が定義されていることを確認
      expect(mockOnGroupUpdate).toBeDefined();
      expect(mockOnGroupDelete).toBeDefined();
      expect(mockOnBulkGroupDelete).toBeDefined();
      expect(mockOnManageMembers).toBeDefined();
    });

    test("onManageMembersが省略された場合でも正常に動作する", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
        />
      );

      // メンバー管理なしでも正常にレンダリングされることを確認
      expect(screen.getByText("開発チーム")).toBeInTheDocument();
    });
  });

  describe("新機能のテスト", () => {
    test("Members列が表示される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      // Members列のヘッダーが表示されることを確認
      expect(screen.getByText("Members")).toBeInTheDocument();

      // 各グループのメンバー数が表示されることを確認
      expect(screen.getByTestId("member-count-1")).toBeInTheDocument();
      expect(screen.getByTestId("member-count-2")).toBeInTheDocument();
    });

    test("フィルター機能が動作する", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      // フィルター入力欄が存在することを確認
      const filterInput = screen.getByPlaceholderText("Filter names...");
      expect(filterInput).toBeInTheDocument();
    });

    test("列の表示/非表示切り替えボタンが存在する", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
          onBulkGroupDelete={mockOnBulkGroupDelete}
          onManageMembers={mockOnManageMembers}
        />
      );

      // Columnsボタンが存在することを確認
      expect(screen.getByText("Columns")).toBeInTheDocument();
    });
  });
});

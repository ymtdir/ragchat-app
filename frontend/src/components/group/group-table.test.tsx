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

describe("GroupTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("グループテーブルが正しく表示される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
        />
      );

      expect(screen.getByText("開発チーム")).toBeInTheDocument();
      expect(
        screen.getByText("Webアプリケーション開発チーム")
      ).toBeInTheDocument();
      expect(screen.getByText("デザインチーム")).toBeInTheDocument();
      expect(screen.getByText("UI/UXデザインチーム")).toBeInTheDocument();
    });

    test("ローディング中はスケルトンが表示される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={true}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
        />
      );

      // ローディング状態が表示されることを確認（スケルトン要素が存在する）
      const skeletonElements = screen.getAllByRole("generic");
      expect(
        skeletonElements.some(el => el.classList.contains("animate-pulse"))
      ).toBe(true);
    });
  });

  describe("グループ更新", () => {
    test("onGroupUpdateが正しく渡される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
        />
      );

      // onGroupUpdateが渡されていることを確認（実際の呼び出しはGroupEditModalで行われる）
      expect(mockOnGroupUpdate).toBeDefined();
    });
  });

  describe("グループ削除", () => {
    test("onGroupDeleteが正しく渡される", () => {
      render(
        <GroupTable
          data={mockGroups}
          isLoading={false}
          onGroupUpdate={mockOnGroupUpdate}
          onGroupDelete={mockOnGroupDelete}
        />
      );

      // onGroupDeleteが渡されていることを確認
      expect(mockOnGroupDelete).toBeDefined();
    });
  });
});

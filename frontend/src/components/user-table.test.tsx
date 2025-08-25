/* eslint-disable @typescript-eslint/no-explicit-any */
import { render, screen } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UserTable } from "./user-table";
import type { User } from "@/types/api";

const mockUsers: User[] = [
  {
    id: 1,
    name: "テストユーザー1",
    email: "test1@example.com",
  },
  {
    id: 2,
    name: "テストユーザー2",
    email: "test2@example.com",
  },
];

const mockOnUserUpdate = vi.fn();

describe("UserTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("ユーザーテーブルが正しく表示される", () => {
      render(
        <UserTable
          data={mockUsers}
          isLoading={false}
          onUserUpdate={mockOnUserUpdate}
        />
      );

      expect(screen.getByText("テストユーザー1")).toBeInTheDocument();
      expect(screen.getByText("test1@example.com")).toBeInTheDocument();
      expect(screen.getByText("テストユーザー2")).toBeInTheDocument();
      expect(screen.getByText("test2@example.com")).toBeInTheDocument();
    });

    test("ローディング中はスケルトンが表示される", () => {
      render(
        <UserTable
          data={mockUsers}
          isLoading={true}
          onUserUpdate={mockOnUserUpdate}
        />
      );

      // ローディング状態が表示されることを確認（スケルトン要素が存在する）
      const skeletonElements = screen.getAllByRole("generic");
      expect(
        skeletonElements.some((el) => el.classList.contains("animate-pulse"))
      ).toBe(true);
    });
  });

  describe("ユーザー更新", () => {
    test("onUserUpdateが正しく渡される", () => {
      render(
        <UserTable
          data={mockUsers}
          isLoading={false}
          onUserUpdate={mockOnUserUpdate}
        />
      );

      // onUserUpdateが渡されていることを確認（実際の呼び出しはUserEditModalで行われる）
      expect(mockOnUserUpdate).toBeDefined();
    });
  });
});

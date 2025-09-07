import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UserBulkDeleteDialog } from "./user-bulk-delete-dialog";
import type { User } from "@/types/api";

const mockUsers: User[] = [
  { id: 1, name: "テストユーザー1", email: "test1@example.com" },
  { id: 2, name: "テストユーザー2", email: "test2@example.com" },
  { id: 3, name: "テストユーザー3", email: "test3@example.com" },
];

const defaultProps = {
  selectedUsers: mockUsers,
  isOpen: true,
  onClose: vi.fn(),
  onConfirm: vi.fn(),
  onLoadingChange: vi.fn(),
};

describe("UserBulkDeleteDialog", () => {
  beforeEach(() => {
    // fetchをモック化
    global.fetch = vi.fn();
  });

  describe("レンダリング", () => {
    test("ダイアログが正しく表示される", () => {
      render(<UserBulkDeleteDialog {...defaultProps} />);

      expect(
        screen.getByText("選択したユーザーを一括削除")
      ).toBeInTheDocument();
      expect(
        screen.getByText(/選択した 3 件のユーザーを削除しますか？/)
      ).toBeInTheDocument();
      expect(screen.getByText("キャンセル")).toBeInTheDocument();
      expect(screen.getByText("3件を削除")).toBeInTheDocument();
    });

    test("ダイアログが閉じている場合は何も表示しない", () => {
      render(<UserBulkDeleteDialog {...defaultProps} isOpen={false} />);

      expect(
        screen.queryByText("選択したユーザーを一括削除")
      ).not.toBeInTheDocument();
    });

    test("選択されたユーザーが0件の場合は安全に表示される", () => {
      render(<UserBulkDeleteDialog {...defaultProps} selectedUsers={[]} />);

      expect(
        screen.getByText("選択したユーザーを一括削除")
      ).toBeInTheDocument();
      expect(
        screen.getByText(/選択した 0 件のユーザーを削除しますか？/)
      ).toBeInTheDocument();
      expect(screen.getByText("0件を削除")).toBeInTheDocument();
    });
  });

  describe("ボタン操作", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<UserBulkDeleteDialog {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });

    test("削除ボタンをクリックするとAPIが呼ばれ、成功時にonConfirm(true)が呼ばれる", async () => {
      const onConfirm = vi.fn();
      const onLoadingChange = vi.fn();

      // 成功レスポンスをモック
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
        json: async () => ({
          message: "ユーザーが正常に削除されました",
          deleted_count: 1,
        }),
      });

      render(
        <UserBulkDeleteDialog
          {...defaultProps}
          onConfirm={onConfirm}
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("3件を削除");
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(onLoadingChange).toHaveBeenCalledWith(true);
        expect(onLoadingChange).toHaveBeenCalledWith(false);
        expect(onConfirm).toHaveBeenCalledWith(true);
      });

      // 3つのユーザーに対してAPIが呼ばれることを確認
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/1",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/2",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/3",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
    });

    test("削除ボタンをクリックするとAPIが呼ばれ、失敗時にonConfirm(false)が呼ばれる", async () => {
      const onConfirm = vi.fn();
      const onLoadingChange = vi.fn();

      // 失敗レスポンスをモック
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({ detail: "ユーザーが見つかりません" }),
      });

      render(
        <UserBulkDeleteDialog
          {...defaultProps}
          onConfirm={onConfirm}
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("3件を削除");
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(onLoadingChange).toHaveBeenCalledWith(true);
        expect(onLoadingChange).toHaveBeenCalledWith(false);
        expect(onConfirm).toHaveBeenCalledWith(false);
      });
    });
  });

  describe("ローディング状態", () => {
    test("削除処理中はボタンが無効化され、テキストが変わる", async () => {
      const onLoadingChange = vi.fn();

      // 遅延レスポンスをモック
      (global.fetch as ReturnType<typeof vi.fn>).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  json: async () => ({
                    message: "ユーザーが正常に削除されました",
                    deleted_count: 1,
                  }),
                }),
              100
            )
          )
      );

      render(
        <UserBulkDeleteDialog
          {...defaultProps}
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("3件を削除");
      fireEvent.click(deleteButton);

      // ローディング状態を確認
      await waitFor(() => {
        expect(screen.getByText("削除中...")).toBeInTheDocument();
        expect(screen.queryByText("3件を削除")).not.toBeInTheDocument();
      });

      const cancelButton = screen.getByText("キャンセル");
      const loadingDeleteButton = screen.getByText("削除中...");

      expect(cancelButton).toBeDisabled();
      expect(loadingDeleteButton).toBeDisabled();
    });
  });
});

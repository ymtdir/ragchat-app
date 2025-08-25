import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UserDeleteDialog } from "./user-delete-dialog";
import type { User } from "@/types/api";

const mockUser: User = {
  id: 1,
  name: "テストユーザー",
  email: "test@example.com",
};

const defaultProps = {
  user: mockUser,
  isOpen: true,
  onClose: vi.fn(),
  onConfirm: vi.fn(),
  onLoadingChange: vi.fn(),
};

describe("UserDeleteDialog", () => {
  beforeEach(() => {
    // fetchをモック化
    global.fetch = vi.fn();
  });

  describe("レンダリング", () => {
    test("ダイアログが正しく表示される", () => {
      render(<UserDeleteDialog {...defaultProps} />);

      expect(screen.getByText("ユーザーを削除")).toBeInTheDocument();
      expect(
        screen.getByText(/ユーザー "テストユーザー" を削除しますか？/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/この操作は取り消すことができません。/)
      ).toBeInTheDocument();
      expect(screen.getByText("キャンセル")).toBeInTheDocument();
      expect(screen.getByText("削除")).toBeInTheDocument();
    });

    test("ダイアログが閉じている場合は何も表示しない", () => {
      render(<UserDeleteDialog {...defaultProps} isOpen={false} />);

      expect(screen.queryByText("ユーザーを削除")).not.toBeInTheDocument();
    });

    test("ユーザーがnullの場合は安全に表示される", () => {
      render(<UserDeleteDialog {...defaultProps} user={null} />);

      expect(screen.getByText("ユーザーを削除")).toBeInTheDocument();
      expect(
        screen.getByText(/ユーザー "" を削除しますか？/)
      ).toBeInTheDocument();
    });
  });

  describe("ボタン操作", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<UserDeleteDialog {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });

    test("削除ボタンをクリックするとAPIが呼ばれ、成功時にonConfirm(true)が呼ばれる", async () => {
      const onConfirm = vi.fn();
      const onLoadingChange = vi.fn();
      
      // 成功レスポンスをモック
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "ユーザーが正常に削除されました", deleted_count: 1 }),
      });

      render(
        <UserDeleteDialog 
          {...defaultProps} 
          onConfirm={onConfirm} 
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("削除");
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(onLoadingChange).toHaveBeenCalledWith(true);
        expect(onLoadingChange).toHaveBeenCalledWith(false);
        expect(onConfirm).toHaveBeenCalledWith(true);
      });

      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/users/1",
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
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({ detail: "ID 1 のユーザーが見つかりません" }),
      });

      render(
        <UserDeleteDialog 
          {...defaultProps} 
          onConfirm={onConfirm} 
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("削除");
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
      (global.fetch as ReturnType<typeof vi.fn>).mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ message: "ユーザーが正常に削除されました", deleted_count: 1 }),
        }), 100))
      );

      render(
        <UserDeleteDialog 
          {...defaultProps} 
          onLoadingChange={onLoadingChange}
        />
      );

      const deleteButton = screen.getByText("削除");
      fireEvent.click(deleteButton);

      // ローディング状態を確認
      await waitFor(() => {
        expect(screen.getByText("削除中...")).toBeInTheDocument();
        expect(screen.queryByText("削除")).not.toBeInTheDocument();
      });

      const cancelButton = screen.getByText("キャンセル");
      const loadingDeleteButton = screen.getByText("削除中...");

      expect(cancelButton).toBeDisabled();
      expect(loadingDeleteButton).toBeDisabled();
    });
  });
});

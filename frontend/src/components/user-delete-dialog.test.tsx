import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, describe, vi } from "vitest";
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
  isLoading: false,
};

describe("UserDeleteDialog", () => {
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

    test("削除ボタンをクリックするとonConfirmが呼ばれる", () => {
      const onConfirm = vi.fn();
      render(<UserDeleteDialog {...defaultProps} onConfirm={onConfirm} />);

      const deleteButton = screen.getByText("削除");
      fireEvent.click(deleteButton);

      expect(onConfirm).toHaveBeenCalled();
    });
  });

  describe("ローディング状態", () => {
    test("ローディング中はボタンが無効化される", () => {
      render(<UserDeleteDialog {...defaultProps} isLoading={true} />);

      const cancelButton = screen.getByText("キャンセル");
      const deleteButton = screen.getByText("削除中...");

      expect(cancelButton).toBeDisabled();
      expect(deleteButton).toBeDisabled();
    });

    test("ローディング中は削除ボタンのテキストが変わる", () => {
      render(<UserDeleteDialog {...defaultProps} isLoading={true} />);

      expect(screen.getByText("削除中...")).toBeInTheDocument();
      expect(screen.queryByText("削除")).not.toBeInTheDocument();
    });
  });
});

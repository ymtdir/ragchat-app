import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UserEditModal } from "./user-edit-modal";
import type { User } from "@/types/api";

// fetchのモック
global.fetch = vi.fn();

const mockUser: User = {
  id: 1,
  name: "テストユーザー",
  email: "test@example.com",
};

const defaultProps = {
  user: mockUser,
  isOpen: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
};

describe("UserEditModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("ユーザーがnullの場合は何も表示しない", () => {
      render(<UserEditModal {...defaultProps} user={null} />);
      expect(screen.queryByText("ユーザー編集")).not.toBeInTheDocument();
    });

    test("モーダルが開いている場合は正しく表示される", () => {
      render(<UserEditModal {...defaultProps} />);
      expect(screen.getByText("ユーザー編集")).toBeInTheDocument();
      expect(screen.getAllByText("アカウント")).toHaveLength(2); // タブボタンとカードタイトル
      expect(screen.getByText("パスワード")).toBeInTheDocument();
    });

    test("ユーザー情報が正しく表示される", () => {
      render(<UserEditModal {...defaultProps} />);
      expect(screen.getByDisplayValue("テストユーザー")).toBeInTheDocument();
      expect(screen.getByDisplayValue("test@example.com")).toBeInTheDocument();
    });
  });

  describe("アカウント情報の編集", () => {
    test("名前を変更できる", () => {
      render(<UserEditModal {...defaultProps} />);
      const nameInput = screen.getByDisplayValue("テストユーザー");
      fireEvent.change(nameInput, { target: { value: "新しい名前" } });
      expect(nameInput).toHaveValue("新しい名前");
    });

    test("メールアドレスを変更できる", () => {
      render(<UserEditModal {...defaultProps} />);
      const emailInput = screen.getByDisplayValue("test@example.com");
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      expect(emailInput).toHaveValue("new@example.com");
    });
  });

  describe("パスワードの変更", () => {
    test("パスワードタブが存在する", () => {
      render(<UserEditModal {...defaultProps} />);
      expect(screen.getByText("パスワード")).toBeInTheDocument();
    });
  });

  describe("バリデーション", () => {
    test("名前が3文字未満の場合エラーが表示される", () => {
      render(<UserEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストユーザー");
      fireEvent.change(nameInput, { target: { value: "ab" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      expect(
        screen.getByText("名前は3文字以上で入力してください")
      ).toBeInTheDocument();
    });

    test("無効なメールアドレスの場合エラーが表示される", () => {
      render(<UserEditModal {...defaultProps} />);

      const emailInput = screen.getByDisplayValue("test@example.com");
      fireEvent.change(emailInput, { target: { value: "invalid-email" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      expect(
        screen.getByText("有効なメールアドレスを入力してください")
      ).toBeInTheDocument();
    });
  });

  describe("キャンセル機能", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<UserEditModal {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });
  });
});

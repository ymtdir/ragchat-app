import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { UserCreateModal } from "./user-create-modal";
import type { User } from "@/types/api";

// fetchのモック
global.fetch = vi.fn();

const mockUser: User = {
  id: 1,
  name: "新しいユーザー",
  email: "new@example.com",
  created_at: "2024-01-01T10:00:00Z",
  updated_at: "2024-01-01T10:00:00Z",
  deleted_at: null,
};

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
};

describe("UserCreateModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("モーダルが開いている場合は正しく表示される", () => {
      render(<UserCreateModal {...defaultProps} />);
      expect(screen.getByText("ユーザー作成")).toBeInTheDocument();
      expect(screen.getByText("ユーザー情報")).toBeInTheDocument();
    });

    test("モーダルが閉じている場合は何も表示しない", () => {
      render(<UserCreateModal {...defaultProps} isOpen={false} />);
      expect(screen.queryByText("ユーザー作成")).not.toBeInTheDocument();
    });

    test("入力フィールドが正しく表示される", () => {
      render(<UserCreateModal {...defaultProps} />);
      expect(screen.getByLabelText("名前")).toBeInTheDocument();
      expect(screen.getByLabelText("メールアドレス")).toBeInTheDocument();
    });
  });

  describe("アカウント情報の入力", () => {
    test("名前を入力できる", () => {
      render(<UserCreateModal {...defaultProps} />);
      const nameInput = screen.getByLabelText("名前");
      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      expect(nameInput).toHaveValue("新しいユーザー");
    });

    test("メールアドレスを入力できる", () => {
      render(<UserCreateModal {...defaultProps} />);
      const emailInput = screen.getByLabelText("メールアドレス");
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      expect(emailInput).toHaveValue("new@example.com");
    });
  });

  describe("パスワードの入力", () => {
    test("パスワードを入力できる", () => {
      render(<UserCreateModal {...defaultProps} />);
      const passwordInput = screen.getByLabelText("パスワード");
      fireEvent.change(passwordInput, { target: { value: "password123" } });
      expect(passwordInput).toHaveValue("password123");
    });

    test("パスワード確認を入力できる", () => {
      render(<UserCreateModal {...defaultProps} />);
      const confirmInput = screen.getByLabelText("パスワード（確認）");
      fireEvent.change(confirmInput, { target: { value: "password123" } });
      expect(confirmInput).toHaveValue("password123");
    });
  });

  describe("バリデーション", () => {
    test("名前が3文字未満の場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      fireEvent.change(nameInput, { target: { value: "ab" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("名前は3文字以上で入力してください")
      ).toBeInTheDocument();
    });

    test("メールアドレスが空の場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("メールアドレスを入力してください")
      ).toBeInTheDocument();
    });

    test("無効なメールアドレスの場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "invalid-email" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("有効なメールアドレスを入力してください")
      ).toBeInTheDocument();
    });

    test("パスワードが空の場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("パスワードを入力してください")
      ).toBeInTheDocument();
    });

    test("パスワードが8文字未満の場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      const passwordInput = screen.getByLabelText("パスワード");
      const confirmInput = screen.getByLabelText("パスワード（確認）");

      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      fireEvent.change(passwordInput, { target: { value: "short" } });
      fireEvent.change(confirmInput, { target: { value: "short" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("パスワードは8文字以上で入力してください")
      ).toBeInTheDocument();
    });

    test("パスワードが一致しない場合エラーが表示される", () => {
      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      const passwordInput = screen.getByLabelText("パスワード");
      const confirmInput = screen.getByLabelText("パスワード（確認）");

      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      fireEvent.change(passwordInput, { target: { value: "password123" } });
      fireEvent.change(confirmInput, { target: { value: "different" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(screen.getByText("パスワードが一致しません")).toBeInTheDocument();
    });
  });

  describe("API呼び出し", () => {
    test("作成成功時にAPIが呼ばれる", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      } as Response);

      render(<UserCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      const passwordInput = screen.getByLabelText("パスワード");
      const confirmInput = screen.getByLabelText("パスワード（確認）");

      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      fireEvent.change(passwordInput, { target: { value: "password123" } });
      fireEvent.change(confirmInput, { target: { value: "password123" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith("/api/users/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: "新しいユーザー",
            email: "new@example.com",
            password: "password123",
          }),
        });
      });
    });

    test("作成成功時にonSaveが呼ばれる", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      } as Response);

      const onSave = vi.fn();
      render(<UserCreateModal {...defaultProps} onSave={onSave} />);

      const nameInput = screen.getByLabelText("名前");
      const emailInput = screen.getByLabelText("メールアドレス");
      const passwordInput = screen.getByLabelText("パスワード");
      const confirmInput = screen.getByLabelText("パスワード（確認）");

      fireEvent.change(nameInput, { target: { value: "新しいユーザー" } });
      fireEvent.change(emailInput, { target: { value: "new@example.com" } });
      fireEvent.change(passwordInput, { target: { value: "password123" } });
      fireEvent.change(confirmInput, { target: { value: "password123" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(mockUser);
      });
    });
  });

  describe("キャンセル機能", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<UserCreateModal {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });
  });
});

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupCreateModal } from "./group-create-modal";
import type { Group } from "@/types/api";

// fetchのモック
global.fetch = vi.fn();

const mockGroup: Group = {
  id: 1,
  name: "新規グループ",
  description: "新規グループの説明",
  created_at: "2024-01-01T10:00:00Z",
  updated_at: "2024-01-01T10:00:00Z",
  deleted_at: null,
};

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
};

describe("GroupCreateModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("モーダルが開いている場合は正しく表示される", () => {
      render(<GroupCreateModal {...defaultProps} />);
      expect(screen.getByText("グループ作成")).toBeInTheDocument();
      expect(screen.getByText("グループ情報")).toBeInTheDocument();
    });

    test("モーダルが閉じている場合は何も表示しない", () => {
      render(<GroupCreateModal {...defaultProps} isOpen={false} />);
      expect(screen.queryByText("グループ作成")).not.toBeInTheDocument();
    });

    test("入力フィールドが正しく表示される", () => {
      render(<GroupCreateModal {...defaultProps} />);
      expect(screen.getByLabelText("グループ名 *")).toBeInTheDocument();
      expect(screen.getByLabelText("説明（任意）")).toBeInTheDocument();
    });
  });

  describe("グループ情報の入力", () => {
    test("グループ名を入力できる", () => {
      render(<GroupCreateModal {...defaultProps} />);
      const nameInput = screen.getByLabelText("グループ名 *");
      fireEvent.change(nameInput, { target: { value: "新規グループ" } });
      expect(nameInput).toHaveValue("新規グループ");
    });

    test("説明を入力できる", () => {
      render(<GroupCreateModal {...defaultProps} />);
      const descriptionInput = screen.getByLabelText("説明（任意）");
      fireEvent.change(descriptionInput, {
        target: { value: "グループの説明" },
      });
      expect(descriptionInput).toHaveValue("グループの説明");
    });
  });

  describe("バリデーション", () => {
    test("グループ名が空の場合エラーが表示される", () => {
      render(<GroupCreateModal {...defaultProps} />);

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("グループ名を入力してください")
      ).toBeInTheDocument();
    });

    test("グループ名が100文字を超える場合エラーが表示される", () => {
      render(<GroupCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      const longName = "a".repeat(101);
      fireEvent.change(nameInput, { target: { value: longName } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      expect(
        screen.getByText("グループ名は100文字以内で入力してください")
      ).toBeInTheDocument();
    });

    test("説明は任意のため空でもエラーにならない", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockGroup,
      } as Response);

      render(<GroupCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      fireEvent.change(nameInput, { target: { value: "新規グループ" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // エラーメッセージが表示されないことを確認
      await waitFor(() => {
        expect(screen.queryByText(/エラー/)).not.toBeInTheDocument();
      });
    });
  });

  describe("API呼び出し", () => {
    test("作成成功時にAPIが呼ばれる（説明あり）", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockGroup,
      } as Response);

      render(<GroupCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      const descriptionInput = screen.getByLabelText("説明（任意）");

      fireEvent.change(nameInput, { target: { value: "新規グループ" } });
      fireEvent.change(descriptionInput, {
        target: { value: "新規グループの説明" },
      });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          "http://localhost:8000/api/groups/",
          {
            method: "POST",
            headers: {
              Authorization: "Bearer null",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: "新規グループ",
              description: "新規グループの説明",
            }),
          }
        );
      });
    });

    test("作成成功時にAPIが呼ばれる（説明なし）", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockGroup,
      } as Response);

      render(<GroupCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      fireEvent.change(nameInput, { target: { value: "新規グループ" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          "http://localhost:8000/api/groups/",
          {
            method: "POST",
            headers: {
              Authorization: "Bearer null",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: "新規グループ",
              description: undefined,
            }),
          }
        );
      });
    });

    test("作成成功時にonSaveが呼ばれる", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockGroup,
      } as Response);

      const onSave = vi.fn();
      render(<GroupCreateModal {...defaultProps} onSave={onSave} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      fireEvent.change(nameInput, { target: { value: "新規グループ" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(mockGroup);
      });
    });

    test("API呼び出し失敗時にエラーメッセージが表示される", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error("Network error")
      );

      render(<GroupCreateModal {...defaultProps} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      fireEvent.change(nameInput, { target: { value: "新規グループ" } });

      const createButton = screen.getByText("作成");
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText("Network error")).toBeInTheDocument();
      });
    });
  });

  describe("キャンセル機能", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<GroupCreateModal {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });
  });

  describe("フォームリセット", () => {
    test("モーダルが開かれるたびにフォームがリセットされる", () => {
      const { rerender } = render(
        <GroupCreateModal {...defaultProps} isOpen={false} />
      );

      // まず開いた状態にしてフォームに入力
      rerender(<GroupCreateModal {...defaultProps} isOpen={true} />);

      const nameInput = screen.getByLabelText("グループ名 *");
      const descriptionInput = screen.getByLabelText("説明（任意）");

      fireEvent.change(nameInput, { target: { value: "テストグループ" } });
      fireEvent.change(descriptionInput, { target: { value: "テスト説明" } });

      // 一度閉じて再度開く
      rerender(<GroupCreateModal {...defaultProps} isOpen={false} />);
      rerender(<GroupCreateModal {...defaultProps} isOpen={true} />);

      // フォームがリセットされていることを確認
      const newNameInput = screen.getByLabelText("グループ名 *");
      const newDescriptionInput = screen.getByLabelText("説明（任意）");

      expect(newNameInput).toHaveValue("");
      expect(newDescriptionInput).toHaveValue("");
    });
  });
});

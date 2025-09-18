import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupEditModal } from "./group-edit-modal";
import type { Group } from "@/types/api";

// fetchのモック
global.fetch = vi.fn();

const mockGroup: Group = {
  id: 1,
  name: "テストグループ",
  description: "テストグループの説明",
  created_at: "2024-01-01T10:00:00Z",
  updated_at: "2024-01-01T10:00:00Z",
  deleted_at: null,
};

const mockGroupWithoutDescription: Group = {
  id: 2,
  name: "説明なしグループ",
  description: null,
  created_at: "2024-01-02T10:00:00Z",
  updated_at: "2024-01-02T10:00:00Z",
  deleted_at: null,
};

const defaultProps = {
  group: mockGroup,
  isOpen: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
};

describe("GroupEditModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("レンダリング", () => {
    test("グループがnullの場合は何も表示しない", () => {
      render(<GroupEditModal {...defaultProps} group={null} />);
      expect(screen.queryByText("グループ編集")).not.toBeInTheDocument();
    });

    test("モーダルが開いている場合は正しく表示される", () => {
      render(<GroupEditModal {...defaultProps} />);
      expect(screen.getByText("グループ編集")).toBeInTheDocument();
      expect(screen.getByText("グループ情報")).toBeInTheDocument();
    });

    test("グループ情報が正しく表示される", () => {
      render(<GroupEditModal {...defaultProps} />);
      expect(screen.getByDisplayValue("テストグループ")).toBeInTheDocument();
      expect(
        screen.getByDisplayValue("テストグループの説明")
      ).toBeInTheDocument();
    });

    test("説明がnullの場合は空文字で表示される", () => {
      render(
        <GroupEditModal {...defaultProps} group={mockGroupWithoutDescription} />
      );
      expect(screen.getByDisplayValue("説明なしグループ")).toBeInTheDocument();

      const descriptionInput = screen.getByLabelText(
        "説明（任意）"
      ) as HTMLTextAreaElement;
      expect(descriptionInput.value).toBe("");
    });
  });

  describe("グループ情報の編集", () => {
    test("グループ名を変更できる", () => {
      render(<GroupEditModal {...defaultProps} />);
      const nameInput = screen.getByDisplayValue("テストグループ");
      fireEvent.change(nameInput, { target: { value: "新しいグループ名" } });
      expect(nameInput).toHaveValue("新しいグループ名");
    });

    test("説明を変更できる", () => {
      render(<GroupEditModal {...defaultProps} />);
      const descriptionInput = screen.getByDisplayValue("テストグループの説明");
      fireEvent.change(descriptionInput, { target: { value: "新しい説明" } });
      expect(descriptionInput).toHaveValue("新しい説明");
    });
  });

  describe("バリデーション", () => {
    test("グループ名が空の場合エラーが表示される", () => {
      render(<GroupEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      fireEvent.change(nameInput, { target: { value: "" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      expect(
        screen.getByText("グループ名を入力してください")
      ).toBeInTheDocument();
    });

    test("グループ名が100文字を超える場合エラーが表示される", () => {
      render(<GroupEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      const longName = "a".repeat(101);
      fireEvent.change(nameInput, { target: { value: longName } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      expect(
        screen.getByText("グループ名は100文字以内で入力してください")
      ).toBeInTheDocument();
    });
  });

  describe("API呼び出し", () => {
    test("更新成功時にAPIが呼ばれる（名前のみ変更）", async () => {
      const updatedGroup = { ...mockGroup, name: "更新されたグループ" };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedGroup,
      } as Response);

      render(<GroupEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      fireEvent.change(nameInput, { target: { value: "更新されたグループ" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          "http://localhost:8000/api/groups/1",
          {
            method: "PUT",
            headers: {
              Authorization: "Bearer null",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: "更新されたグループ",
            }),
          }
        );
      });
    });

    test("更新成功時にAPIが呼ばれる（説明のみ変更）", async () => {
      const updatedGroup = { ...mockGroup, description: "更新された説明" };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedGroup,
      } as Response);

      render(<GroupEditModal {...defaultProps} />);

      const descriptionInput = screen.getByDisplayValue("テストグループの説明");
      fireEvent.change(descriptionInput, {
        target: { value: "更新された説明" },
      });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          "http://localhost:8000/api/groups/1",
          {
            method: "PUT",
            headers: {
              Authorization: "Bearer null",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              description: "更新された説明",
            }),
          }
        );
      });
    });

    test("更新成功時にAPIが呼ばれる（名前と説明両方変更）", async () => {
      const updatedGroup = {
        ...mockGroup,
        name: "更新されたグループ",
        description: "更新された説明",
      };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedGroup,
      } as Response);

      render(<GroupEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      const descriptionInput = screen.getByDisplayValue("テストグループの説明");

      fireEvent.change(nameInput, { target: { value: "更新されたグループ" } });
      fireEvent.change(descriptionInput, {
        target: { value: "更新された説明" },
      });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          "http://localhost:8000/api/groups/1",
          {
            method: "PUT",
            headers: {
              Authorization: "Bearer null",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: "更新されたグループ",
              description: "更新された説明",
            }),
          }
        );
      });
    });

    test("更新成功時にonSaveが呼ばれる", async () => {
      const updatedGroup = { ...mockGroup, name: "更新されたグループ" };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedGroup,
      } as Response);

      const onSave = vi.fn();
      render(<GroupEditModal {...defaultProps} onSave={onSave} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      fireEvent.change(nameInput, { target: { value: "更新されたグループ" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      // 非同期処理を待つ
      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(updatedGroup);
      });
    });

    test("変更がない場合はAPIを呼ばずにモーダルを閉じる", () => {
      const onClose = vi.fn();
      render(<GroupEditModal {...defaultProps} onClose={onClose} />);

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      expect(fetch).not.toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });

    test("API呼び出し失敗時にエラーメッセージが表示される", async () => {
      (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error("Network error")
      );

      render(<GroupEditModal {...defaultProps} />);

      const nameInput = screen.getByDisplayValue("テストグループ");
      fireEvent.change(nameInput, { target: { value: "更新されたグループ" } });

      const saveButton = screen.getByText("保存");
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText("Network error")).toBeInTheDocument();
      });
    });
  });

  describe("キャンセル機能", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<GroupEditModal {...defaultProps} onClose={onClose} />);

      const cancelButton = screen.getByText("キャンセル");
      fireEvent.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });
  });

  describe("フォーム初期化", () => {
    test("グループが変更されるとフォームが更新される", () => {
      const { rerender } = render(<GroupEditModal {...defaultProps} />);

      // 最初のグループの値を確認
      expect(screen.getByDisplayValue("テストグループ")).toBeInTheDocument();
      expect(
        screen.getByDisplayValue("テストグループの説明")
      ).toBeInTheDocument();

      // 別のグループに変更
      const newGroup: Group = {
        id: 3,
        name: "別のグループ",
        description: "別の説明",
        created_at: "2024-01-03T10:00:00Z",
        updated_at: "2024-01-03T10:00:00Z",
        deleted_at: null,
      };

      rerender(<GroupEditModal {...defaultProps} group={newGroup} />);

      // 新しいグループの値が表示されることを確認
      expect(screen.getByDisplayValue("別のグループ")).toBeInTheDocument();
      expect(screen.getByDisplayValue("別の説明")).toBeInTheDocument();
    });
  });
});

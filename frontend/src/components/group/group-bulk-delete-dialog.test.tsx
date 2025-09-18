import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupBulkDeleteDialog } from "./group-bulk-delete-dialog";
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
  {
    id: 3,
    name: "マーケティングチーム",
    description: "マーケティング戦略チーム",
    created_at: "2024-01-03T10:00:00Z",
    updated_at: "2024-01-03T10:00:00Z",
    deleted_at: null,
  },
];

const defaultProps = {
  selectedGroups: mockGroups,
  isOpen: true,
  onClose: vi.fn(),
  onConfirm: vi.fn(),
  onLoadingChange: vi.fn(),
};

describe("GroupBulkDeleteDialog", () => {
  beforeEach(() => {
    // fetchをモック化
    global.fetch = vi.fn();
  });

  describe("レンダリング", () => {
    test("ダイアログが正しく表示される", () => {
      render(<GroupBulkDeleteDialog {...defaultProps} />);

      expect(
        screen.getByText("選択したグループを一括削除")
      ).toBeInTheDocument();
      expect(
        screen.getByText(/選択した 3 件のグループを削除しますか？/)
      ).toBeInTheDocument();
      expect(screen.getByText("キャンセル")).toBeInTheDocument();
      expect(screen.getByText("3件を削除")).toBeInTheDocument();
    });

    test("ダイアログが閉じている場合は何も表示しない", () => {
      render(<GroupBulkDeleteDialog {...defaultProps} isOpen={false} />);

      expect(
        screen.queryByText("選択したグループを一括削除")
      ).not.toBeInTheDocument();
    });

    test("選択されたグループが0件の場合は安全に表示される", () => {
      render(<GroupBulkDeleteDialog {...defaultProps} selectedGroups={[]} />);

      expect(
        screen.getByText("選択したグループを一括削除")
      ).toBeInTheDocument();
      expect(
        screen.getByText(/選択した 0 件のグループを削除しますか？/)
      ).toBeInTheDocument();
      expect(screen.getByText("0件を削除")).toBeInTheDocument();
    });
  });

  describe("ボタン操作", () => {
    test("キャンセルボタンをクリックするとonCloseが呼ばれる", () => {
      const onClose = vi.fn();
      render(<GroupBulkDeleteDialog {...defaultProps} onClose={onClose} />);

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
          message: "グループが正常に削除されました",
          deleted_count: 1,
        }),
      });

      render(
        <GroupBulkDeleteDialog
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

      // 3つのグループに対してAPIが呼ばれることを確認
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/1",
        {
          method: "DELETE",
          headers: {
            Authorization: "Bearer null",
            "Content-Type": "application/json",
          },
        }
      );
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/2",
        {
          method: "DELETE",
          headers: {
            Authorization: "Bearer null",
            "Content-Type": "application/json",
          },
        }
      );
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/groups/3",
        {
          method: "DELETE",
          headers: {
            Authorization: "Bearer null",
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
        json: async () => ({ detail: "グループが見つかりません" }),
      });

      render(
        <GroupBulkDeleteDialog
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

    test("一部が成功し一部が失敗した場合にonConfirm(false)が呼ばれる", async () => {
      const onConfirm = vi.fn();
      const onLoadingChange = vi.fn();

      // 最初の2つは成功、最後は失敗
      (global.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            message: "グループが正常に削除されました",
            deleted_count: 1,
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            message: "グループが正常に削除されました",
            deleted_count: 1,
          }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 404,
          json: async () => ({ detail: "グループが見つかりません" }),
        });

      render(
        <GroupBulkDeleteDialog
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

    test("ネットワークエラー時にonConfirm(false)が呼ばれる", async () => {
      const onConfirm = vi.fn();
      const onLoadingChange = vi.fn();

      // ネットワークエラーをモック
      (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error("Network error")
      );

      render(
        <GroupBulkDeleteDialog
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
          new Promise(resolve =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  json: async () => ({
                    message: "グループが正常に削除されました",
                    deleted_count: 1,
                  }),
                }),
              100
            )
          )
      );

      render(
        <GroupBulkDeleteDialog
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

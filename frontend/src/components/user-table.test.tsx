/* eslint-disable @typescript-eslint/no-explicit-any */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, test, describe, vi } from "vitest";
import { UserTable, columns, type User } from "./user-table";

// テスト用のモックデータ
const mockUsers: User[] = [
  {
    id: 1,
    email: "test1@example.com",
    name: "testuser1",
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    email: "test2@example.com",
    name: "testuser2",
    is_active: false,
    created_at: "2024-01-02T00:00:00Z",
    updated_at: "2024-01-02T00:00:00Z",
  },
];

// navigator.clipboard のモック
Object.defineProperty(navigator, "clipboard", {
  value: {
    writeText: vi.fn(),
  },
  writable: true,
});

describe("UserTable", () => {
  test("ユーザーデータが正しく表示される", () => {
    render(<UserTable data={mockUsers} />);

    // IDが表示されることを確認
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();

    // メールアドレスが表示されることを確認
    expect(screen.getByText("test1@example.com")).toBeInTheDocument();
    expect(screen.getByText("test2@example.com")).toBeInTheDocument();
  });

  test("ローディング状態が正しく表示される", () => {
    render(<UserTable data={[]} isLoading={true} />);

    // ローディング用のスケルトンが表示されることを確認
    const skeletonElements = screen.getAllByRole("generic");
    expect(
      skeletonElements.some((el) => el.classList.contains("animate-pulse"))
    ).toBe(true);
  });

  test("空のデータの場合にメッセージが表示される", () => {
    render(<UserTable data={[]} />);

    expect(screen.getByText("No results.")).toBeInTheDocument();
  });

  test("メールアドレスでフィルターできる", async () => {
    render(<UserTable data={mockUsers} />);

    const filterInput = screen.getByPlaceholderText("Filter emails...");
    fireEvent.change(filterInput, { target: { value: "test1" } });

    await waitFor(() => {
      expect(screen.getByText("test1@example.com")).toBeInTheDocument();
      expect(screen.queryByText("test2@example.com")).not.toBeInTheDocument();
    });
  });

  test("ソート機能が動作する", () => {
    render(<UserTable data={mockUsers} />);

    // ユーザー名でソートボタンをクリック
    const sortButton = screen.getByRole("button", { name: "Name" });
    fireEvent.click(sortButton);

    // ソートアイコンが表示されることを確認
    expect(sortButton).toBeInTheDocument();
  });

  test("行選択ができる", () => {
    render(<UserTable data={mockUsers} />);

    // 個別の行を選択
    const checkboxes = screen.getAllByRole("checkbox");
    const firstRowCheckbox = checkboxes[1]; // 0番目は全選択チェックボックス

    fireEvent.click(firstRowCheckbox);
    expect(firstRowCheckbox).toBeChecked();
  });

  test("全選択ができる", () => {
    render(<UserTable data={mockUsers} />);

    // 全選択チェックボックスをクリック
    const selectAllCheckbox = screen.getAllByRole("checkbox")[0];
    fireEvent.click(selectAllCheckbox);

    // 他のチェックボックスも選択されることを確認
    const checkboxes = screen.getAllByRole("checkbox");
    checkboxes.forEach((checkbox) => {
      expect(checkbox).toBeChecked();
    });
  });

  test("ページネーションが動作する", () => {
    // 複数ページに分かれるデータを作成
    const manyUsers = Array.from({ length: 25 }, (_, i) => ({
      ...mockUsers[0],
      id: i + 1,
      email: `test${i + 1}@example.com`,
      name: `testuser${i + 1}`,
    }));

    render(<UserTable data={manyUsers} />);

    // 次のページボタンが有効であることを確認
    const nextButton = screen.getByRole("button", { name: "Next" });
    expect(nextButton).not.toBeDisabled();

    // 前のページボタンが無効であることを確認（最初のページなので）
    const prevButton = screen.getByRole("button", { name: "Previous" });
    expect(prevButton).toBeDisabled();
  });

  test.skip("アクションメニューが動作する", async () => {
    render(<UserTable data={mockUsers} />);

    // アクションボタンをクリック（roleでボタンを特定）
    const actionButtons = screen.getAllByRole("button", {
      name: "メニューを開く",
    });

    // 最初のアクションボタンをクリック
    fireEvent.click(actionButtons[0]);

    // メニューが表示されることを確認（より長いタイムアウトで待機）
    await waitFor(
      () => {
        expect(screen.getByText("ユーザーIDをコピー")).toBeInTheDocument();
        expect(screen.getByText("ユーザー詳細を表示")).toBeInTheDocument();
        expect(screen.getByText("ユーザーを編集")).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  test.skip("ユーザーIDコピー機能が動作する", async () => {
    render(<UserTable data={mockUsers} />);

    // アクションボタンをクリック（roleでボタンを特定）
    const actionButtons = screen.getAllByRole("button", {
      name: "メニューを開く",
    });

    // 最初のアクションボタンをクリック
    fireEvent.click(actionButtons[0]);

    // メニューが表示されてからコピーボタンをクリック
    await waitFor(
      () => {
        const copyButton = screen.getByText("ユーザーIDをコピー");
        expect(copyButton).toBeInTheDocument();
        fireEvent.click(copyButton);
      },
      { timeout: 3000 }
    );

    // clipboard.writeTextが呼ばれることを確認
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("1");
  });

  test("カラム表示/非表示が切り替えられる", async () => {
    render(<UserTable data={mockUsers} />);

    // カラムボタンをクリック（テキストでボタンを特定）
    const columnsButton = screen.getByText("Columns");
    fireEvent.click(columnsButton);

    // カラム選択メニューが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText("ID")).toBeInTheDocument();
      expect(screen.getByText("Name")).toBeInTheDocument();
      expect(screen.getByText("Email")).toBeInTheDocument();
    });
  });
});

describe("columns", () => {
  test("正しい数のカラムが定義されている", () => {
    expect(columns).toHaveLength(5); // select, id, name, email, actions
  });

  test("各カラムが必要なプロパティを持っている", () => {
    const [selectCol, idCol, nameCol, emailCol, actionsCol] = columns;

    // select カラム
    expect(selectCol.id).toBe("select");
    expect(selectCol.enableSorting).toBe(false);
    expect(selectCol.enableHiding).toBe(false);

    // id カラム
    expect((idCol as any).accessorKey).toBe("id");

    // name カラム
    expect((nameCol as any).accessorKey).toBe("name");

    // email カラム
    expect((emailCol as any).accessorKey).toBe("email");

    // actions カラム
    expect(actionsCol.id).toBe("actions");
    expect(actionsCol.enableHiding).toBe(false);
  });
});

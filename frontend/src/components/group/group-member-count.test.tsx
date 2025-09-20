import { render, screen, waitFor } from "@testing-library/react";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { GroupMemberCount } from "./group-member-count";
import { MembershipService } from "@/services/membership-service";

// MembershipServiceをモック
vi.mock("@/services/membership-service", () => ({
  MembershipService: {
    getGroupMemberCount: vi.fn(),
  },
}));

describe("GroupMemberCount", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // コンソールエラーをモック化してテスト出力をクリーンに保つ
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("正常な表示", () => {
    test("メンバー数が正しく表示される", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(5);

      const { container } = render(<GroupMemberCount groupId={1} />);

      // ローディング状態が最初に表示される（パルスアニメーション）
      const loadingElement = container.querySelector(".animate-pulse");
      expect(loadingElement).toBeInTheDocument();

      // メンバー数が表示されるまで待機
      await waitFor(() => {
        expect(screen.getByText("5")).toBeInTheDocument();
      });

      // ローディングアニメーションが消える
      expect(container.querySelector(".animate-pulse")).not.toBeInTheDocument();
    });

    test("メンバー数が0の場合", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(0);

      render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("0")).toBeInTheDocument();
      });
    });

    test("メンバー数が多い場合", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(100);

      render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("100")).toBeInTheDocument();
      });
    });

    test("正しいgroupIdでAPIが呼ばれる", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(3);

      render(<GroupMemberCount groupId={42} />);

      await waitFor(() => {
        expect(MembershipService.getGroupMemberCount).toHaveBeenCalledWith(42);
      });
    });
  });

  describe("エラーハンドリング", () => {
    test("APIエラー時にエラー表示される", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockRejectedValue(
        new Error("ネットワークエラー")
      );

      const { container } = render(<GroupMemberCount groupId={1} />);

      // エラーが表示されるまで待機（"-"が表示される）
      await waitFor(() => {
        expect(screen.getByText("-")).toBeInTheDocument();
      });

      // ローディングアニメーションが消える
      expect(container.querySelector(".animate-pulse")).not.toBeInTheDocument();
    });

    test("認証エラー時", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockRejectedValue(
        new Error("認証に失敗しました")
      );

      render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("-")).toBeInTheDocument();
      });
    });

    test("サーバーエラー時", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockRejectedValue(
        new Error("Internal Server Error")
      );

      render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("-")).toBeInTheDocument();
      });
    });
  });

  describe("ローディング状態", () => {
    test("初期状態でローディングが表示される", () => {
      // APIレスポンスを遅延させる
      vi.mocked(MembershipService.getGroupMemberCount).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(3), 1000))
      );

      const { container } = render(<GroupMemberCount groupId={1} />);

      expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
      expect(screen.queryByText("3")).not.toBeInTheDocument();
    });

    test("ローディング中にpulseアニメーションが表示される", () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(3), 1000))
      );

      const { container } = render(<GroupMemberCount groupId={1} />);

      expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
    });
  });

  describe("再レンダリング", () => {
    test("groupIdが変更された時に再度APIが呼ばれる", async () => {
      vi.mocked(MembershipService.getGroupMemberCount)
        .mockResolvedValueOnce(3)
        .mockResolvedValueOnce(7);

      const { rerender } = render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("3")).toBeInTheDocument();
      });

      // groupIdを変更
      rerender(<GroupMemberCount groupId={2} />);

      await waitFor(() => {
        expect(screen.getByText("7")).toBeInTheDocument();
      });

      expect(MembershipService.getGroupMemberCount).toHaveBeenCalledTimes(2);
      expect(MembershipService.getGroupMemberCount).toHaveBeenNthCalledWith(
        1,
        1
      );
      expect(MembershipService.getGroupMemberCount).toHaveBeenNthCalledWith(
        2,
        2
      );
    });

    test("同じgroupIdの場合はAPIが再度呼ばれない", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(3);

      const { rerender } = render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("3")).toBeInTheDocument();
      });

      // 同じgroupIdで再レンダリング
      rerender(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("3")).toBeInTheDocument();
      });

      // APIは1回だけ呼ばれる
      expect(MembershipService.getGroupMemberCount).toHaveBeenCalledTimes(1);
    });
  });

  describe("UI要素", () => {
    test("メンバー数が正しく表示される", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(5);

      render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(screen.getByText("5")).toBeInTheDocument();
      });
    });

    test("コンポーネントが正常にレンダリングされる", async () => {
      vi.mocked(MembershipService.getGroupMemberCount).mockResolvedValue(5);

      const { container } = render(<GroupMemberCount groupId={1} />);

      await waitFor(() => {
        expect(container.firstChild).toBeInTheDocument();
      });
    });
  });
});

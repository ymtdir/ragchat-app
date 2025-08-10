import { useNavigate } from "react-router-dom";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function useAuth() {
  const navigate = useNavigate();

  const logout = async () => {
    try {
      const token = localStorage.getItem("access_token");

      // ログアウトAPIを呼び出し
      const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        console.error("ログアウトAPIエラー:", response.status);
      }
    } catch (error) {
      console.error("ログアウト処理エラー:", error);
    } finally {
      // エラーが発生してもローカルストレージのトークンは削除
      localStorage.removeItem("access_token");
      navigate("/signin");
    }
  };

  return {
    logout,
  };
}

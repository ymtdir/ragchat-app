import { useNavigate } from "react-router-dom";

export function useAuth() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("access_token");
    navigate("/signin");
  };

  return {
    logout,
  };
}

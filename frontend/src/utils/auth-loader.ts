import { redirect } from "react-router-dom";
import type { RouteObject } from "react-router-dom";

export function requireAuth() {
  const token = localStorage.getItem("access_token");
  if (!token) throw redirect("/signin");
  return { token };
}

export function requireGuest() {
  const token = localStorage.getItem("access_token");
  if (token) throw redirect("/dashboard");
  return null;
}

// ルートヘルパー関数
export function guestRoute(
  path: string,
  element: React.ReactNode
): RouteObject {
  return { path, element, loader: requireGuest };
}

export function protectedRoute(
  path: string,
  element: React.ReactNode
): RouteObject {
  return { path, element, loader: requireAuth };
}

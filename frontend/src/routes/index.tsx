import { SignInForm } from "@/pages/signin-form";
import { SignUpForm } from "@/pages/signup-form";
import { Dashboard } from "@/pages/dashboard";
import { UsersPage } from "@/pages/users";
import { guestRoute, protectedRoute } from "@/utils/auth-loader";

export const createGuestRoutes = () => [
  guestRoute("/", <SignInForm />),
  guestRoute("/signin", <SignInForm />),
  guestRoute("/signup", <SignUpForm />),
];

export const createProtectedRoutes = () => [
  protectedRoute("/dashboard", <Dashboard />),
  protectedRoute("/users", <UsersPage />),
];

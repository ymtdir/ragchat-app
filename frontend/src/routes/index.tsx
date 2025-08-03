import { SignInForm } from "@/components/signin-form";
import { SignUpForm } from "@/components/signup-form";
import { Dashboard } from "@/components/dashboard";
import { guestRoute, protectedRoute } from "@/utils/auth-loader";

export const createGuestRoutes = () => [
  guestRoute("/", <SignInForm />),
  guestRoute("/signin", <SignInForm />),
  guestRoute("/signup", <SignUpForm />),
];

export const createProtectedRoutes = () => [
  protectedRoute("/dashboard", <Dashboard />),
];

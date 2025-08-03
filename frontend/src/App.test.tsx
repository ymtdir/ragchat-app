import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { SignInForm } from "@/components/signin-form";
import { SignUpForm } from "@/components/signup-form";
import App from "./App";

// React Routerのモック
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// テスト用のラッパーコンポーネント
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe("サインインフォーム", () => {
  test("フォームフィールドが正しく表示される", () => {
    render(<SignInForm />);

    expect(screen.getByText("Sign in to your account")).toBeTruthy();
    expect(screen.getByLabelText("Email")).toBeTruthy();
    expect(screen.getByLabelText("Password")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
    expect(screen.getByText("Don't have an account?")).toBeTruthy();
    expect(screen.getByText("Sign up")).toBeTruthy();
  });

  test("フォームフィールドに入力できる", async () => {
    const user = userEvent.setup();
    render(<SignInForm />);

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");

    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
  });

  test("必須フィールドが正しく設定されている", () => {
    render(<SignInForm />);

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");

    expect(emailInput).toHaveAttribute("required");
    expect(passwordInput).toHaveAttribute("required");
  });

  test("emailフィールドが正しいタイプを持つ", () => {
    render(<SignInForm />);

    const emailInput = screen.getByLabelText("Email");
    expect(emailInput).toHaveAttribute("type", "email");
  });

  test("passwordフィールドが正しいタイプを持つ", () => {
    render(<SignInForm />);

    const passwordInput = screen.getByLabelText("Password");
    expect(passwordInput).toHaveAttribute("type", "password");
  });

  test("フォーム送信ボタンが正しく表示される", () => {
    render(<SignInForm />);

    const submitButton = screen.getByRole("button", { name: "Sign in" });
    expect(submitButton).toHaveAttribute("type", "submit");
  });
});

describe("サインアップフォーム", () => {
  test("フォームが正しくレンダリングされる", () => {
    render(<SignUpForm />);

    expect(screen.getByText("Create an account")).toBeTruthy();
    expect(screen.getByLabelText("Name")).toBeTruthy();
    expect(screen.getByLabelText("Email")).toBeTruthy();
    expect(screen.getByLabelText("Password")).toBeTruthy();
    expect(screen.getByLabelText("Confirm password")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Sign up" })).toBeTruthy();
    expect(screen.getByText("Already have an account?")).toBeTruthy();
    expect(screen.getByText("Sign in")).toBeTruthy();
  });

  test("フォームフィールドに入力できる", async () => {
    const user = userEvent.setup();
    render(<SignUpForm />);

    const nameInput = screen.getByLabelText("Name");
    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const confirmPasswordInput = screen.getByLabelText("Confirm password");

    await user.type(nameInput, "Test User");
    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    expect(nameInput).toHaveValue("Test User");
    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
    expect(confirmPasswordInput).toHaveValue("password123");
  });

  test("必須フィールドが正しく設定されている", () => {
    render(<SignUpForm />);

    const nameInput = screen.getByLabelText("Name");
    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const confirmPasswordInput = screen.getByLabelText("Confirm password");

    expect(nameInput).toHaveAttribute("required");
    expect(emailInput).toHaveAttribute("required");
    expect(passwordInput).toHaveAttribute("required");
    expect(confirmPasswordInput).toHaveAttribute("required");
  });

  test("emailフィールドが正しいタイプを持つ", () => {
    render(<SignUpForm />);

    const emailInput = screen.getByLabelText("Email");
    expect(emailInput).toHaveAttribute("type", "email");
  });

  test("passwordフィールドが正しいタイプを持つ", () => {
    render(<SignUpForm />);

    const passwordInput = screen.getByLabelText("Password");
    const confirmPasswordInput = screen.getByLabelText("Confirm password");

    expect(passwordInput).toHaveAttribute("type", "password");
    expect(confirmPasswordInput).toHaveAttribute("type", "password");
  });

  test("パスワードが一致しない場合エラーが表示される", async () => {
    const user = userEvent.setup();
    render(<SignUpForm />);

    const nameInput = screen.getByLabelText("Name");
    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const confirmPasswordInput = screen.getByLabelText("Confirm password");
    const submitButton = screen.getByRole("button", { name: "Sign up" });

    await user.type(nameInput, "Test User");
    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "differentpassword");

    await user.click(submitButton);

    expect(screen.getByText("Passwords do not match")).toBeTruthy();
  });

  test("パスワードが一致する場合エラーが表示されない", async () => {
    const user = userEvent.setup();
    render(<SignUpForm />);

    const nameInput = screen.getByLabelText("Name");
    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");
    const confirmPasswordInput = screen.getByLabelText("Confirm password");
    const submitButton = screen.getByRole("button", { name: "Sign up" });

    await user.type(nameInput, "Test User");
    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    await user.click(submitButton);

    // エラーメッセージが表示されないことを確認
    expect(screen.queryByText("Passwords do not match")).toBeNull();
  });
});

describe("App", () => {
  test("アプリケーションが正常にレンダリングされる", () => {
    render(<App />);

    // ルーターが正しく設定されていることを確認
    expect(screen.getByText("Sign in to your account")).toBeTruthy();
  });
});

describe("認証統合テスト", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  test("サインインフォームがRouterコンテキスト内で正常に動作する", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    expect(screen.getByText("Sign in to your account")).toBeTruthy();
    expect(screen.getByLabelText("Email")).toBeTruthy();
    expect(screen.getByLabelText("Password")).toBeTruthy();
  });

  test("サインアップフォームがRouterコンテキスト内で正常に動作する", () => {
    render(
      <TestWrapper>
        <SignUpForm />
      </TestWrapper>
    );

    expect(screen.getByText("Create an account")).toBeTruthy();
    expect(screen.getByLabelText("Name")).toBeTruthy();
    expect(screen.getByLabelText("Email")).toBeTruthy();
  });
});

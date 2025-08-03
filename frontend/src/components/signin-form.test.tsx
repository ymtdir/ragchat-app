import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test, describe, vi } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { SignInForm } from "./signin-form";

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

describe("SignInFormコンポーネント", () => {
  test("フォームが正しくレンダリングされる", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    expect(screen.getByText("Sign in to your account")).toBeTruthy();
    expect(screen.getByLabelText("Email")).toBeTruthy();
    expect(screen.getByLabelText("Password")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
    expect(screen.getByText("Don't have an account?")).toBeTruthy();
    expect(screen.getByText("Sign up")).toBeTruthy();
  });

  test("フォームフィールドに入力できる", async () => {
    const user = userEvent.setup();
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");

    expect(emailInput).toHaveValue("test@example.com");
    expect(passwordInput).toHaveValue("password123");
  });

  test("必須フィールドが正しく設定されている", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText("Email");
    const passwordInput = screen.getByLabelText("Password");

    expect(emailInput).toHaveAttribute("required");
    expect(passwordInput).toHaveAttribute("required");
  });

  test("emailフィールドが正しいタイプを持つ", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText("Email");
    expect(emailInput).toHaveAttribute("type", "email");
  });

  test("passwordフィールドが正しいタイプを持つ", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText("Password");
    expect(passwordInput).toHaveAttribute("type", "password");
  });

  test("フォーム送信ボタンが正しく表示される", () => {
    render(
      <TestWrapper>
        <SignInForm />
      </TestWrapper>
    );

    const submitButton = screen.getByRole("button", { name: "Sign in" });
    expect(submitButton).toHaveAttribute("type", "submit");
  });
});

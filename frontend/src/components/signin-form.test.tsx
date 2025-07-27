import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test, describe } from "vitest";
import { SignInForm } from "./signin-form";

describe("SignInFormコンポーネント", () => {
  test("フォームが正しくレンダリングされる", () => {
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

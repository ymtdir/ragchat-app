import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test, describe, vi, beforeEach } from "vitest";
import { SignUpForm } from "./signup-form";

// fetchのモック
global.fetch = vi.fn();

describe("SignUpFormコンポーネント", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

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

  test("API呼び出しが正しく行われる", async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response);

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

    expect(mockFetch).toHaveBeenCalledWith("/api/users/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Test User",
        email: "test@example.com",
        password: "password123",
      }),
    });
  });

  test("APIエラー時にエラーメッセージが表示される", async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Email already exists" }),
    } as Response);

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

    expect(screen.getByText("Email already exists")).toBeTruthy();
  });

  test("ネットワークエラー時にエラーメッセージが表示される", async () => {
    const mockFetch = vi.mocked(fetch);
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

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

    expect(screen.getByText("通信エラーが発生しました")).toBeTruthy();
  });
});

import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test } from "vitest";
import App from "./App";

test("Appコンポーネントがレンダリングされる", () => {
  render(<App />);
  expect(screen.getByText("Vite + React")).toBeTruthy();
});

test("カウントボタンが表示される", () => {
  render(<App />);
  expect(screen.getByRole("button")).toBeTruthy();
  expect(screen.getByText("count is 0")).toBeTruthy();
});

test("ボタンをクリックするとカウントが増える", async () => {
  const user = userEvent.setup();
  render(<App />);

  const button = screen.getByRole("button");
  expect(screen.getByText("count is 0")).toBeTruthy();

  await user.click(button);
  expect(screen.getByText("count is 1")).toBeTruthy();

  await user.click(button);
  expect(screen.getByText("count is 2")).toBeTruthy();
});

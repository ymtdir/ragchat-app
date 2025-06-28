import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";

// テスト用のAppコンポーネントを定義
function App() {
  return <h1>Hello World</h1>;
}

describe("App", () => {
  it("Hello World が表示される", () => {
    render(<App />);
    const heading = screen.getByText("Hello World");
    expect(heading).toBeInTheDocument();
  });

  it("h1タグが正しく表示される", () => {
    render(<App />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent("Hello World");
  });
});

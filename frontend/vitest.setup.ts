import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// window オブジェクトのモック
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// ResizeObserver のモック
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// IntersectionObserver のモック
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// AbortSignalのモック
global.AbortSignal = class AbortSignal {
  static abort() {
    return new AbortSignal();
  }
  static timeout() {
    return new AbortSignal();
  }
  static any() {
    return new AbortSignal();
  }
} as unknown as typeof AbortSignal;

// 未処理のPromise拒否をキャッチ
process.on("unhandledRejection", reason => {
  // AbortSignal関連のエラーを無視
  if (reason && typeof reason === "object" && "message" in reason) {
    const message = (reason as Error).message;
    if (message.includes("AbortSignal") || message.includes("RequestInit")) {
      return;
    }
  }
  // その他のエラーは通常通り処理
  throw reason;
});

// エラーハンドリングを無効化
const originalConsoleError = console.error;
console.error = (...args) => {
  // AbortSignal関連のエラーを抑制
  if (
    typeof args[0] === "string" &&
    (args[0].includes("AbortSignal") || args[0].includes("RequestInit"))
  ) {
    return;
  }
  // その他のエラーは通常通り表示
  originalConsoleError(...args);
};

// テスト環境での警告を抑制
const originalConsoleWarn = console.warn;
console.warn = (...args) => {
  // DialogContentのアクセシビリティ警告を抑制
  if (
    typeof args[0] === "string" &&
    (args[0].includes("Missing `Description` or `aria-describedby") ||
      args[0].includes("HydrateFallback"))
  ) {
    return;
  }
  // その他の警告は通常通り表示
  originalConsoleWarn(...args);
};

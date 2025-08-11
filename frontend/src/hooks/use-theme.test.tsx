import React from "react";
import { renderHook } from "@testing-library/react";
import { expect, test, describe } from "vitest";
import { useTheme, ThemeProviderContext, type Theme } from "./use-theme";

// モックコンテキスト値
const mockContextValue = {
  theme: "light" as Theme,
  setTheme: () => {},
};

// コンテキストプロバイダーでラップするヘルパー
const createWrapper = (contextValue = mockContextValue) => {
  return ({ children }: { children: React.ReactNode }) => (
    <ThemeProviderContext.Provider value={contextValue}>
      {children}
    </ThemeProviderContext.Provider>
  );
};

describe("useTheme", () => {
  test("コンテキストが提供されている場合、コンテキストの値を返す", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(result.current).toEqual(mockContextValue);
  });

  test("コンテキストが提供されていない場合、デフォルト値が使用される", () => {
    // プロバイダーなしでuseThemeを使用した場合のテスト
    const { result } = renderHook(() => useTheme());

    // デフォルトコンテキストの値を確認
    expect(result.current.theme).toBe("system");
    expect(typeof result.current.setTheme).toBe("function");
  });

  test("異なるテーマ値でも正しく動作する", () => {
    const darkThemeContext = {
      theme: "dark" as Theme,
      setTheme: () => {},
    };

    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(darkThemeContext),
    });

    expect(result.current.theme).toBe("dark");
  });

  test("systemテーマでも正しく動作する", () => {
    const systemThemeContext = {
      theme: "system" as Theme,
      setTheme: () => {},
    };

    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(systemThemeContext),
    });

    expect(result.current.theme).toBe("system");
  });

  test("setTheme関数が提供される", () => {
    const mockSetTheme = () => {};
    const contextWithSetTheme = {
      theme: "light" as Theme,
      setTheme: mockSetTheme,
    };

    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(contextWithSetTheme),
    });

    expect(result.current.setTheme).toBe(mockSetTheme);
    expect(typeof result.current.setTheme).toBe("function");
  });
});

describe("ThemeProviderContext", () => {
  test("デフォルト値が正しく設定されている", () => {
    // ThemeProviderContextのデフォルト値をrenderHook経由で確認
    const { result } = renderHook(() => useTheme());

    // デフォルトコンテキストの値を確認
    expect(result.current.theme).toBe("system");
    expect(typeof result.current.setTheme).toBe("function");
  });
});

describe("Theme type", () => {
  test("正しいテーマタイプが定義されている", () => {
    const themes: Theme[] = ["light", "dark", "system"];

    themes.forEach((theme) => {
      const contextValue = {
        theme,
        setTheme: () => {},
      };

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper(contextValue),
      });

      expect(result.current.theme).toBe(theme);
    });
  });
});

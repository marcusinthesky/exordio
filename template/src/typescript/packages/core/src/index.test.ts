import { expect, test } from "bun:test";
import { greet } from "./index";

test("a display name is normalized", () => {
  expect(greet(" Ada ")).toBe("Hello, Ada!");
});

test("an empty display name is rejected", () => {
  expect(() => greet(" ")).toThrow("non-whitespace");
});

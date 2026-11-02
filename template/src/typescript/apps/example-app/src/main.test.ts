import { expect, test } from "bun:test";
import { fileURLToPath } from "node:url";

test("the application consumes the workspace library", () => {
  const result = Bun.spawnSync([
    process.execPath,
    fileURLToPath(new URL("./main.ts", import.meta.url)),
    "Grace",
  ]);
  expect(result.exitCode).toBe(0);
  expect(new TextDecoder().decode(result.stdout)).toBe("Hello, Grace!\n");
});

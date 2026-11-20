import { readdir, readFile, writeFile } from "node:fs/promises";

// Drizzle emits SQL without a final newline; normalize it only when authoring.
const directory = new URL("../drizzle/", import.meta.url);
for (const entry of await readdir(directory, { withFileTypes: true })) {
  if (!entry.isFile() || !entry.name.endsWith(".sql")) continue;
  const file = new URL(entry.name, directory);
  const content = await readFile(file, "utf8");
  if (!content.endsWith("\n")) await writeFile(file, `${content}\n`);
}

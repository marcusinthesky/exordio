import { readFile, stat } from "node:fs/promises";
import { createServer } from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(
  new URL("../packages/ui/storybook-static/", import.meta.url),
);
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};
await stat(path.join(root, "iframe.html"));
createServer(async (request, response) => {
  try {
    const url = new URL(request.url ?? "/", "http://localhost");
    const filename = path.resolve(
      root,
      `.${decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname)}`,
    );
    if (!filename.startsWith(root)) throw new Error("Outside static directory");
    const body = await readFile(filename);
    response.writeHead(200, {
      "Content-Type":
        types[path.extname(filename)] ?? "application/octet-stream",
      "Cache-Control": "no-store",
    });
    response.end(body);
  } catch {
    response.writeHead(404);
    response.end("Not found");
  }
}).listen(6006, "127.0.0.1", () => {
  console.log("Serving built Storybook at http://127.0.0.1:6006");
});

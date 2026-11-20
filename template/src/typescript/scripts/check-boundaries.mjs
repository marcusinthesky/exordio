import { readdir, readFile, realpath } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const root = fileURLToPath(new URL("../", import.meta.url));
const ui = path.join(root, "packages/ui");
const sourceRoot = path.join(ui, "src");
const manifest = JSON.parse(
  await readFile(path.join(ui, "package.json"), "utf8"),
);
const dependencies = new Set([
  ...Object.keys(manifest.dependencies ?? {}),
  ...Object.keys(manifest.peerDependencies ?? {}),
]);
const errors = [];

async function* sources(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const filename = path.join(directory, entry.name);
    if (entry.isDirectory()) yield* sources(filename);
    else if (
      /\.(tsx?|jsx?)$/.test(entry.name) &&
      !/\.(stories|test)\./.test(entry.name)
    ) {
      yield filename;
    }
  }
}

function checkImport(specifier, filename) {
  const relative = path.relative(root, filename);
  const fail = (reason) => errors.push(`${relative}: ${specifier} — ${reason}`);
  if (
    /^(next(?:\/|$)|server-only$|better-auth(?:\/|$)|drizzle-orm(?:\/|$)|pg$|@exordio\/web(?:\/|$)|node:)/.test(
      specifier,
    )
  ) {
    fail("UI must be independent of the application and server runtime");
  } else if (specifier.startsWith(".")) {
    const destination = path.resolve(path.dirname(filename), specifier);
    if (!destination.startsWith(`${sourceRoot}${path.sep}`)) {
      fail("relative import escapes the UI source boundary");
    }
  } else if (!specifier.startsWith("@exordio/ui/")) {
    const packageName = specifier.startsWith("@")
      ? specifier.split("/").slice(0, 2).join("/")
      : specifier.split("/")[0];
    if (!dependencies.has(packageName))
      fail("runtime dependency is not declared by packages/ui");
  }
}

for await (const filename of sources(sourceRoot)) {
  const resolved = await realpath(filename);
  if (!resolved.startsWith(`${sourceRoot}${path.sep}`)) {
    errors.push(`${filename}: symlink escapes the UI source boundary`);
    continue;
  }
  const source = ts.createSourceFile(
    filename,
    await readFile(filename, "utf8"),
    ts.ScriptTarget.Latest,
    true,
  );
  function visit(node) {
    if (
      (ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) &&
      node.moduleSpecifier &&
      ts.isStringLiteral(node.moduleSpecifier)
    ) {
      checkImport(node.moduleSpecifier.text, filename);
    }
    if (
      ts.isImportTypeNode(node) &&
      ts.isLiteralTypeNode(node.argument) &&
      ts.isStringLiteral(node.argument.literal)
    ) {
      checkImport(node.argument.literal.text, filename);
    }
    if (
      ts.isCallExpression(node) &&
      (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
        (ts.isIdentifier(node.expression) &&
          node.expression.text === "require"))
    ) {
      const argument = node.arguments[0];
      if (argument && ts.isStringLiteral(argument))
        checkImport(argument.text, filename);
      else
        errors.push(
          `${filename}: computed module loading cannot be checked at the UI boundary`,
        );
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
}
if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log("UI dependency boundary passed.");
}

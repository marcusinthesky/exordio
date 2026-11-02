/** Return a greeting after rejecting an empty display name. */
export function greet(name: string): string {
  const cleaned = name.trim();
  if (cleaned.length === 0) {
    throw new Error("name must contain a non-whitespace character");
  }
  return `Hello, ${cleaned}!`;
}

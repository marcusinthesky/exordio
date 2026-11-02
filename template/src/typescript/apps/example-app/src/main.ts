import { greet } from "@example/core";

const name = Bun.argv[2] ?? "world";
console.log(greet(name));

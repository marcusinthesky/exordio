import "server-only";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { getServerEnvironment } from "@/env/server";
import * as schema from "./schema";

const databaseGlobal = globalThis as typeof globalThis & { exordioPool?: Pool };

export function getDb() {
  const env = getServerEnvironment();
  const pool =
    databaseGlobal.exordioPool ??
    new Pool({
      connectionString: env.DATABASE_URL,
      max: 10,
      connectionTimeoutMillis: 5_000,
      idleTimeoutMillis: 30_000,
    });
  databaseGlobal.exordioPool = pool;
  return drizzle(pool, { schema });
}

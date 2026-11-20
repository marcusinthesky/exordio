"use client";

import { createAuthClient } from "better-auth/react";

// Relative requests keep the client on the application's origin.
export const authClient = createAuthClient();

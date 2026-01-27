import { execSync } from "node:child_process";
import { existsSync, rmSync } from "node:fs";
import path from "node:path";
import request from "supertest";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

const testDbPath = path.join(process.cwd(), "test.db");
const databaseUrl = `file:${testDbPath}`;
let prisma: typeof import("../src/db.js").prisma;
let createApp: typeof import("../src/app.js").createApp;

beforeAll(async () => {
  process.env.DATABASE_URL = databaseUrl;
  if (existsSync(testDbPath)) {
    rmSync(testDbPath);
  }
  execSync("npx prisma migrate deploy", {
    cwd: process.cwd(),
    env: { ...process.env, DATABASE_URL: databaseUrl },
    stdio: "inherit"
  });
  ({ prisma } = await import("../src/db.js"));
  ({ createApp } = await import("../src/app.js"));
});

afterAll(async () => {
  if (prisma) {
    await prisma.$disconnect();
  }
  if (existsSync(testDbPath)) {
    rmSync(testDbPath);
  }
});

describe("transactions API", () => {
  it("creates a transaction", async () => {
    const app = createApp();
    const response = await request(app)
      .post("/api/transactions")
      .send({
        type: "EXPENSE",
        date: "2024-08-31",
        amount: 12.5,
        category: "Food",
        description: "Lunch",
        itemLabel: "salad"
      });

    expect(response.status).toBe(201);
    expect(response.body.type).toBe("EXPENSE");
    expect(response.body.amountCents).toBe(1250);
  });

  it("returns summary totals", async () => {
    const app = createApp();
    await prisma.transaction.create({
      data: {
        type: "INFLOW",
        date: new Date("2024-08-30"),
        amountCents: 5000,
        category: "Gift",
        description: "Bonus"
      }
    });

    const response = await request(app).get("/api/summary?from=2024-08-01&to=2024-08-31");

    expect(response.status).toBe(200);
    expect(response.body.inflowTotal).toBeGreaterThanOrEqual(5000);
    expect(response.body.expenseTotal).toBeGreaterThanOrEqual(0);
  });
});

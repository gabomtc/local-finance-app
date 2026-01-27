import express from "express";
import cors from "cors";
import transactionsRouter from "./routes/transactions.js";
import summaryRouter from "./routes/summary.js";

export function createApp() {
  const app = express();

  app.use(cors());
  app.use(express.json());
  app.use("/uploads", express.static("uploads"));

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.use("/api/transactions", transactionsRouter);
  app.use("/api/summary", summaryRouter);

  return app;
}

import { Router } from "express";
import { prisma } from "../db.js";
import { parseDateInput } from "../validation.js";

const router = Router();

router.get("/", async (req, res) => {
  const { from, to } = req.query;

  const where: Record<string, unknown> = {};
  if (from || to) {
    const dateFilter: Record<string, Date> = {};
    if (from && typeof from === "string") {
      const parsed = parseDateInput(from);
      if (!parsed) {
        return res.status(400).json({ error: "Invalid from date" });
      }
      dateFilter.gte = parsed;
    }
    if (to && typeof to === "string") {
      const parsed = parseDateInput(to);
      if (!parsed) {
        return res.status(400).json({ error: "Invalid to date" });
      }
      dateFilter.lte = parsed;
    }
    where.date = dateFilter;
  }

  const [inflows, expenses, overallInflows, overallExpenses, breakdown, recentTransactions] =
    await Promise.all([
    prisma.transaction.aggregate({
      where: { ...where, type: "INFLOW" },
      _sum: { amountCents: true }
    }),
    prisma.transaction.aggregate({
      where: { ...where, type: "EXPENSE" },
      _sum: { amountCents: true }
    }),
    prisma.transaction.aggregate({
      where: { type: "INFLOW" },
      _sum: { amountCents: true }
    }),
    prisma.transaction.aggregate({
      where: { type: "EXPENSE" },
      _sum: { amountCents: true }
    }),
    prisma.transaction.groupBy({
      by: ["category"],
      where: { ...where, type: "EXPENSE" },
      _sum: { amountCents: true }
    }),
    prisma.transaction.findMany({
      where,
      orderBy: { date: "desc" },
      take: 5
    })
  ]);

  const inflowTotal = inflows._sum.amountCents ?? 0;
  const expenseTotal = expenses._sum.amountCents ?? 0;
  const net = inflowTotal - expenseTotal;
  const overallInflowTotal = overallInflows._sum.amountCents ?? 0;
  const overallExpenseTotal = overallExpenses._sum.amountCents ?? 0;
  const currentBalance = overallInflowTotal - overallExpenseTotal;

  return res.json({
    inflowTotal,
    expenseTotal,
    net,
    currentBalance,
    categoryBreakdown: breakdown.map((item) => ({
      category: item.category,
      amountCents: item._sum.amountCents ?? 0
    })),
    recentTransactions
  });
});

export default router;

import { Router } from "express";
import rateLimit from "express-rate-limit";
import { prisma } from "../db.js";
import { createTransactionSchema, parseDateInput, toAmountCents } from "../validation.js";
import { getImageProvider } from "../imageProvider.js";

const router = Router();

router.post("/", async (req, res) => {
  const parsed = createTransactionSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: "Invalid payload", details: parsed.error.flatten() });
  }

  const { type, date, amount, category, description, itemLabel } = parsed.data;
  const parsedDate = parseDateInput(date);
  if (!parsedDate) {
    return res.status(400).json({ error: "Invalid date" });
  }

  if (type === "EXPENSE" && !itemLabel) {
    return res.status(400).json({ error: "itemLabel is required for expenses." });
  }

  const amountCents = toAmountCents(amount);
  if (amountCents <= 0) {
    return res.status(400).json({ error: "Amount must be greater than zero." });
  }

  const transaction = await prisma.transaction.create({
    data: {
      type,
      date: parsedDate,
      amountCents,
      category,
      description,
      itemLabel: type === "EXPENSE" ? itemLabel : null
    }
  });

  return res.status(201).json(transaction);
});

router.get("/", async (req, res) => {
  const { type, category, from, to, limit, offset } = req.query;
  const where: Record<string, unknown> = {};

  if (type) {
    if (type !== "EXPENSE" && type !== "INFLOW") {
      return res.status(400).json({ error: "Invalid type filter" });
    }
    where.type = type;
  }

  if (category) {
    where.category = category;
  }

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

  const take = limit ? Number(limit) : 50;
  const skip = offset ? Number(offset) : 0;

  const [transactions, total] = await Promise.all([
    prisma.transaction.findMany({
      where,
      orderBy: { date: "desc" },
      take,
      skip
    }),
    prisma.transaction.count({ where })
  ]);

  return res.json({ transactions, total });
});

const imageLimiter = rateLimit({
  windowMs: 60_000,
  limit: 5,
  standardHeaders: true,
  legacyHeaders: false
});

router.post("/:id/generate-image", imageLimiter, async (req, res) => {
  const { id } = req.params;
  const transaction = await prisma.transaction.findUnique({ where: { id } });

  if (!transaction) {
    return res.status(404).json({ error: "Transaction not found." });
  }

  if (transaction.type !== "EXPENSE") {
    return res.status(400).json({ error: "Images can only be generated for expenses." });
  }

  if (!transaction.itemLabel) {
    return res.status(400).json({ error: "itemLabel is required to generate an image." });
  }

  const provider = getImageProvider();
  const { imageUrl } = await provider.generateExpenseItemImage({
    itemLabel: transaction.itemLabel,
    category: transaction.category,
    description: transaction.description
  });

  const updated = await prisma.transaction.update({
    where: { id },
    data: { imageUrl }
  });

  return res.json(updated);
});

export default router;

import { z } from "zod";

export const transactionTypeSchema = z.enum(["EXPENSE", "INFLOW"]);

export const createTransactionSchema = z.object({
  type: transactionTypeSchema,
  date: z.string().min(1),
  amount: z.number().positive(),
  category: z.string().min(1),
  description: z.string().min(1),
  itemLabel: z.string().optional()
});

export function parseDateInput(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed;
}

export function toAmountCents(amount: number) {
  return Math.round(amount * 100);
}

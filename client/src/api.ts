export type TransactionType = "EXPENSE" | "INFLOW";

export interface Transaction {
  id: string;
  type: TransactionType;
  date: string;
  amountCents: number;
  category: string;
  description: string;
  itemLabel?: string | null;
  imageUrl?: string | null;
}

export interface SummaryResponse {
  inflowTotal: number;
  expenseTotal: number;
  net: number;
  currentBalance: number;
  categoryBreakdown: Array<{ category: string; amountCents: number }>;
  recentTransactions: Transaction[];
}

export async function fetchTransactions(params: {
  type?: TransactionType | "";
  category?: string;
  from?: string;
  to?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.type) {
    searchParams.set("type", params.type);
  }
  if (params.category) {
    searchParams.set("category", params.category);
  }
  if (params.from) {
    searchParams.set("from", params.from);
  }
  if (params.to) {
    searchParams.set("to", params.to);
  }
  const response = await fetch(`/api/transactions?${searchParams.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to load transactions");
  }
  return (await response.json()) as { transactions: Transaction[]; total: number };
}

export async function createTransaction(payload: {
  type: TransactionType;
  date: string;
  amount: number;
  category: string;
  description: string;
  itemLabel?: string;
}) {
  const response = await fetch("/api/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.error ?? "Failed to create transaction");
  }
  return (await response.json()) as Transaction;
}

export async function fetchSummary(params: { from?: string; to?: string }) {
  const searchParams = new URLSearchParams();
  if (params.from) {
    searchParams.set("from", params.from);
  }
  if (params.to) {
    searchParams.set("to", params.to);
  }
  const response = await fetch(`/api/summary?${searchParams.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to load summary");
  }
  return (await response.json()) as SummaryResponse;
}

export async function generateImage(transactionId: string) {
  const response = await fetch(`/api/transactions/${transactionId}/generate-image`, {
    method: "POST"
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.error ?? "Failed to generate image");
  }
  return (await response.json()) as Transaction;
}

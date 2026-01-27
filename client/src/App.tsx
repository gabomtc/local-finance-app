import { useEffect, useMemo, useState } from "react";
import {
  createTransaction,
  fetchSummary,
  fetchTransactions,
  generateImage,
  Transaction,
  TransactionType
} from "./api";

const categories = ["Coffee", "Groceries", "Transport", "Salary", "Rent", "Utilities"];

function formatCurrency(cents: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD"
  }).format(cents / 100);
}

function todayIso() {
  return new Date().toISOString().split("T")[0];
}

export default function App() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "transactions">("dashboard");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof fetchSummary>> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState({
    type: "",
    category: "",
    from: "",
    to: ""
  });

  const [formState, setFormState] = useState({
    type: "EXPENSE" as TransactionType,
    date: todayIso(),
    amount: "",
    category: "",
    description: "",
    itemLabel: ""
  });

  const requiresItemLabel = formState.type === "EXPENSE";

  const loadTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTransactions(filters);
      setTransactions(data.transactions);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSummary({ from: filters.from, to: filters.to });
      setSummary(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.from, filters.to, filters.category, filters.type]);

  const categoryOptions = useMemo(() => {
    const set = new Set(categories);
    transactions.forEach((transaction) => set.add(transaction.category));
    return Array.from(set.values());
  }, [transactions]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    const amountValue = Number(formState.amount);
    if (!amountValue || amountValue <= 0) {
      setError("Amount must be greater than zero.");
      return;
    }
    if (!formState.category || !formState.description) {
      setError("Category and description are required.");
      return;
    }
    if (requiresItemLabel && !formState.itemLabel) {
      setError("Item label is required for expenses.");
      return;
    }

    try {
      await createTransaction({
        type: formState.type,
        date: formState.date,
        amount: amountValue,
        category: formState.category,
        description: formState.description,
        itemLabel: requiresItemLabel ? formState.itemLabel : undefined
      });
      setFormState((prev) => ({
        ...prev,
        amount: "",
        category: "",
        description: "",
        itemLabel: prev.type === "EXPENSE" ? "" : prev.itemLabel
      }));
      await loadTransactions();
      await loadSummary();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleGenerate = async (transactionId: string) => {
    setLoading(true);
    setError(null);
    try {
      await generateImage(transactionId);
      await loadTransactions();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Local Finance Tracker</h1>
          <p>Track inflows, expenses, and generate item visuals.</p>
        </div>
        <nav className="tabs">
          <button
            className={activeTab === "dashboard" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={activeTab === "transactions" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("transactions")}
          >
            Transactions
          </button>
        </nav>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="panel filters">
        <h2>Filters</h2>
        <div className="filter-grid">
          <label>
            Type
            <select
              value={filters.type}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, type: event.target.value }))
              }
            >
              <option value="">All</option>
              <option value="INFLOW">Inflow</option>
              <option value="EXPENSE">Expense</option>
            </select>
          </label>
          <label>
            Category
            <input
              list="category-options"
              value={filters.category}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, category: event.target.value }))
              }
            />
            <datalist id="category-options">
              {categoryOptions.map((category) => (
                <option value={category} key={category} />
              ))}
            </datalist>
          </label>
          <label>
            From
            <input
              type="date"
              value={filters.from}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, from: event.target.value }))
              }
            />
          </label>
          <label>
            To
            <input
              type="date"
              value={filters.to}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, to: event.target.value }))
              }
            />
          </label>
        </div>
      </section>

      {activeTab === "dashboard" && (
        <main className="dashboard">
          <section className="panel kpis">
            <div>
              <span>Total inflows</span>
              <strong>{summary ? formatCurrency(summary.inflowTotal) : "--"}</strong>
            </div>
            <div>
              <span>Total expenses</span>
              <strong>{summary ? formatCurrency(summary.expenseTotal) : "--"}</strong>
            </div>
            <div>
              <span>Net</span>
              <strong>{summary ? formatCurrency(summary.net) : "--"}</strong>
            </div>
            <div>
              <span>Current balance</span>
              <strong>{summary ? formatCurrency(summary.currentBalance) : "--"}</strong>
            </div>
          </section>

          <section className="panel">
            <h2>Expense breakdown</h2>
            <div className="breakdown">
              {summary?.categoryBreakdown.length ? (
                summary.categoryBreakdown.map((item) => (
                  <div key={item.category} className="breakdown-row">
                    <span>{item.category}</span>
                    <span>{formatCurrency(item.amountCents)}</span>
                    <div className="bar">
                      <div
                        className="fill"
                        style={{
                          width: `${Math.min(
                            100,
                            (item.amountCents /
                              Math.max(
                                ...summary.categoryBreakdown.map((row) => row.amountCents)
                              )) *
                              100
                          )}%`
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="muted">No expense data for the selected range.</p>
              )}
            </div>
          </section>

          <section className="panel">
            <h2>Recent transactions</h2>
            <ul className="transaction-list">
              {summary?.recentTransactions.map((transaction) => (
                <li key={transaction.id}>
                  <div>
                    <strong>{transaction.description}</strong>
                    <span>{transaction.category}</span>
                  </div>
                  <span
                    className={`pill ${
                      transaction.type === "INFLOW" ? "inflow" : "expense"
                    }`}
                  >
                    {transaction.type}
                  </span>
                  <span>{formatCurrency(transaction.amountCents)}</span>
                </li>
              ))}
            </ul>
          </section>
        </main>
      )}

      {activeTab === "transactions" && (
        <main className="transactions">
          <section className="panel">
            <h2>Add transaction</h2>
            <form className="transaction-form" onSubmit={handleSubmit}>
              <label>
                Type
                <select
                  value={formState.type}
                  onChange={(event) =>
                    setFormState((prev) => ({
                      ...prev,
                      type: event.target.value as TransactionType
                    }))
                  }
                >
                  <option value="EXPENSE">Expense</option>
                  <option value="INFLOW">Inflow</option>
                </select>
              </label>
              <label>
                Date
                <input
                  type="date"
                  value={formState.date}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, date: event.target.value }))
                  }
                />
              </label>
              <label>
                Amount
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formState.amount}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, amount: event.target.value }))
                  }
                />
              </label>
              <label>
                Category
                <input
                  list="transaction-category-options"
                  value={formState.category}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, category: event.target.value }))
                  }
                />
                <datalist id="transaction-category-options">
                  {categoryOptions.map((category) => (
                    <option value={category} key={category} />
                  ))}
                </datalist>
              </label>
              <label>
                Description
                <input
                  value={formState.description}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, description: event.target.value }))
                  }
                />
              </label>
              <label>
                Item label
                <input
                  value={formState.itemLabel}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, itemLabel: event.target.value }))
                  }
                  disabled={!requiresItemLabel}
                  placeholder={requiresItemLabel ? "iced coffee" : ""}
                />
              </label>
              <button type="submit" className="primary">
                Add transaction
              </button>
            </form>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2>Transactions</h2>
              {loading && <span className="muted">Loading...</span>}
            </div>
            <div className="transaction-grid">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="transaction-card">
                  <div className="card-header">
                    <div>
                      <h3>{transaction.description}</h3>
                      <p className="muted">
                        {transaction.category} • {transaction.date.split("T")[0]}
                      </p>
                    </div>
                    <span
                      className={`pill ${
                        transaction.type === "INFLOW" ? "inflow" : "expense"
                      }`}
                    >
                      {transaction.type}
                    </span>
                  </div>
                  <p className="amount">{formatCurrency(transaction.amountCents)}</p>
                  {transaction.type === "EXPENSE" && (
                    <div className="image-block">
                      {transaction.imageUrl ? (
                        <a href={transaction.imageUrl} target="_blank" rel="noreferrer">
                          <img
                            src={transaction.imageUrl}
                            alt={transaction.itemLabel ?? "Expense item"}
                          />
                        </a>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleGenerate(transaction.id)}
                          className="secondary"
                        >
                          Generate image
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        </main>
      )}
    </div>
  );
}

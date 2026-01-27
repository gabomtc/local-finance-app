# Local Finance Tracker (TypeScript)

A full-stack personal finance tracker built with React + Vite, Express, and SQLite (Prisma). Capture inflows and expenses, review analytics, and generate AI images for expense items.

## Features

- Record EXPENSE and INFLOW transactions with date, category, description, and amount.
- Expense-only item labels and AI-generated images.
- Dashboard analytics (totals, net, current balance, category breakdown).
- Filterable transaction list with image thumbnails.
- SQLite persistence via Prisma.

## Repo structure

```
/client   # React + Vite frontend
/server   # Express + Prisma backend
```

## Setup

### 1) Install dependencies

```bash
npm install
```

### 2) Configure environment

Create `/server/.env` with:

```
DATABASE_URL="file:./dev.db"
OPENAI_API_KEY="your-key-here"
```

### 3) Migrate the database

```bash
npm run server:prisma:migrate
```

### 4) Seed sample data (optional)

```bash
npm run server:prisma:seed
```

## Run (single command)

```bash
npm run dev
```

- Client: http://localhost:5173
- Server: http://localhost:3001

## API Endpoints

- `POST /api/transactions`
- `GET /api/transactions?type=&category=&from=&to=&limit=&offset=`
- `GET /api/summary?from=&to=`
- `POST /api/transactions/:id/generate-image`

## Tests

```bash
npm run server:test
```

## Notes

- Image generation uses the OpenAI Images API. The provider enforces a photorealistic, neutral background prompt with no logos or copyrighted characters.
- The image generation endpoint is rate-limited to 5 requests per minute per IP.

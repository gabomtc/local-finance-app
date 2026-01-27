import { PrismaClient, TransactionType } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.transaction.deleteMany();

  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  await prisma.transaction.createMany({
    data: [
      {
        type: TransactionType.INFLOW,
        date: today,
        amountCents: 250000,
        category: "Salary",
        description: "Monthly paycheck"
      },
      {
        type: TransactionType.EXPENSE,
        date: yesterday,
        amountCents: 1599,
        category: "Coffee",
        description: "Afternoon pick-me-up",
        itemLabel: "iced coffee"
      },
      {
        type: TransactionType.EXPENSE,
        date: today,
        amountCents: 4200,
        category: "Transport",
        description: "Gas for commute",
        itemLabel: "gasoline"
      }
    ]
  });
}

main()
  .catch((error) => {
    console.error("Seed failed", error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

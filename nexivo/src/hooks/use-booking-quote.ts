"use client";
import { useState } from "react";

type Quote = { amount: string; currency: string; quoteToken: string; selection: string; idempotencyKey: string };
export function useBookingQuote() {
  const [quote, setQuote] = useState<Quote | null>(null);
  async function review(body: Record<string, unknown>) {
    const selection = JSON.stringify(body);
    if (quote?.selection === selection) return { ...body, quoteToken: quote.quoteToken, idempotencyKey: quote.idempotencyKey };
    const response = await fetch("/api/quotes", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error?.message || "A current quote is unavailable.");
    setQuote({ ...result.data, selection, idempotencyKey: crypto.randomUUID() });
    return null;
  }
  return { quote, review, clearQuote: () => setQuote(null) };
}

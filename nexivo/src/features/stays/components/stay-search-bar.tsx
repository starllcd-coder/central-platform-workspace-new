"use client";

import { Search, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useStaySearchStore } from "@/features/stays/store/stay-search.store";

export function StaySearchBar() {
  const { destination, checkIn, checkOut, guests, setDestination, setDates, setGuests } =
    useStaySearchStore();

  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-4 shadow-premium">
      <div className="grid gap-3 lg:grid-cols-[1.4fr_1fr_1fr_0.7fr_auto_auto]">
        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Destination
          </span>
          <Input
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
            placeholder="Search city, area, hotel..."
          />
        </label>

        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Check-in
          </span>
          <Input
            type="date"
            value={checkIn}
            onChange={(event) => setDates(event.target.value, checkOut)}
          />
        </label>

        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Check-out
          </span>
          <Input
            type="date"
            value={checkOut}
            onChange={(event) => setDates(checkIn, event.target.value)}
          />
        </label>

        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Guests
          </span>
          <Input
            type="number"
            min={1}
            value={guests}
            onChange={(event) => setGuests(Number(event.target.value))}
          />
        </label>

        <div className="flex items-end">
          <Button variant="outline" size="lg" className="h-12 w-full">
            <SlidersHorizontal className="mr-2" size={18} />
            Filters
          </Button>
        </div>

        <div className="flex items-end">
          <Button variant="default" size="lg" className="h-12 w-full">
            <Search className="mr-2" size={18} />
            Search
          </Button>
        </div>
      </div>
    </div>
  );
}

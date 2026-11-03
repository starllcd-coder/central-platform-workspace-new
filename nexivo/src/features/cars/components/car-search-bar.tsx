"use client";

import { CalendarDays, MapPin, Search, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCarSearchStore } from "@/features/cars/store/car-search.store";

export function CarSearchBar() {
  const { location, pickupDate, returnDate, setLocation, setDates } = useCarSearchStore();

  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-4 shadow-premium">
      <div className="grid gap-3 lg:grid-cols-[1.5fr_1fr_1fr_auto_auto]">
        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Pickup Location
          </span>
          <Input
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="Airport, city, branch..."
            leftIcon={<MapPin size={17} />}
          />
        </label>

        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Pickup Date
          </span>
          <Input
            type="date"
            value={pickupDate}
            onChange={(event) => setDates(event.target.value, returnDate)}
            leftIcon={<CalendarDays size={17} />}
          />
        </label>

        <label className="space-y-2">
          <span className="px-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
            Return Date
          </span>
          <Input
            type="date"
            value={returnDate}
            onChange={(event) => setDates(pickupDate, event.target.value)}
            leftIcon={<CalendarDays size={17} />}
          />
        </label>

        <div className="flex items-end">
          <Button asChild variant="outline" size="lg" className="h-12 w-full">
            <a href="#car-filters">
              <SlidersHorizontal className="mr-2" size={18} />
              Filters
            </a>
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

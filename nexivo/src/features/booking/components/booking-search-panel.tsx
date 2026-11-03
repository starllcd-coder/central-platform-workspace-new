"use client";

import { CalendarDays, MapPin, Search, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs } from "@/components/ui/tabs";
import { bookingServiceTabs } from "@/features/booking/data/booking-tabs";
import { useBookingSearchStore } from "@/features/booking/store/booking-search.store";
import type { BookingServiceType } from "@/features/booking/data/booking-tabs";
import { cn } from "@/lib/utils";

export function BookingSearchPanel() {
  const {
    service,
    destination,
    checkIn,
    checkOut,
    guests,
    pickupDate,
    returnDate,
    pickupLocation,
    laundryDate,
    laundryAddress,
    setService,
    updateSearch
  } = useBookingSearchStore();

  return (
    <div className="rounded-[1.7rem] border border-luxury-dune/70 bg-white p-4 shadow-[0_24px_70px_rgba(15,23,42,0.13)] backdrop-blur-xl md:p-5">
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-luxury-bronze">
            Search Nexivo
          </p>
          <h2 className="mt-1 font-heading text-xl font-semibold tracking-tight text-luxury-ink">
            Plan the full journey
          </h2>
        </div>

        <span className="w-fit rounded-full border border-luxury-dune bg-luxury-sand/55 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-luxury-bronze">
          StayLux • DriveSphere • Laundrex
        </span>
      </div>

      <Tabs
        variant="premium"
        className="border-luxury-dune/70 bg-luxury-pearl/90 p-1.5 shadow-none"
        value={service}
        onValueChange={(value) => setService(value as BookingServiceType)}
        items={bookingServiceTabs.map((tab) => ({
          value: tab.value,
          label: tab.label,
          icon: <tab.icon size={17} />
        }))}
      />

      <div className="mt-5">
        {service === "stays" ? (
          <div className="grid gap-3 xl:grid-cols-[1.25fr_0.95fr_0.95fr_0.72fr_auto]">
            <FieldShell label="Destination">
              <Input
                value={destination}
                onChange={(event) => updateSearch({ destination: event.target.value })}
                leftIcon={<MapPin size={18} />}
                placeholder="Salalah, Dubai, Doha..."
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 text-base shadow-none"
              />
            </FieldShell>

            <FieldShell label="Check-in">
              <Input
                type="date"
                value={checkIn}
                onChange={(event) => updateSearch({ checkIn: event.target.value })}
                leftIcon={<CalendarDays size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <FieldShell label="Check-out">
              <Input
                type="date"
                value={checkOut}
                onChange={(event) => updateSearch({ checkOut: event.target.value })}
                leftIcon={<CalendarDays size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <FieldShell label="Guests">
              <Input
                type="number"
                min={1}
                value={guests}
                onChange={(event) => updateSearch({ guests: Number(event.target.value) })}
                leftIcon={<UserRound size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <SearchButton href="/stays" />
          </div>
        ) : null}

        {service === "cars" ? (
          <div className="grid gap-3 xl:grid-cols-[1.35fr_0.95fr_0.95fr_auto]">
            <FieldShell label="Pickup location">
              <Input
                value={pickupLocation}
                onChange={(event) => updateSearch({ pickupLocation: event.target.value })}
                leftIcon={<MapPin size={18} />}
                placeholder="Airport, city, branch..."
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 text-base shadow-none"
              />
            </FieldShell>

            <FieldShell label="Pickup date">
              <Input
                type="date"
                value={pickupDate}
                onChange={(event) => updateSearch({ pickupDate: event.target.value })}
                leftIcon={<CalendarDays size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <FieldShell label="Return date">
              <Input
                type="date"
                value={returnDate}
                onChange={(event) => updateSearch({ returnDate: event.target.value })}
                leftIcon={<CalendarDays size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <SearchButton href="/cars" />
          </div>
        ) : null}

        {service === "laundry" ? (
          <div className="grid gap-3 xl:grid-cols-[1.45fr_0.95fr_auto]">
            <FieldShell label="Pickup address or area">
              <Input
                value={laundryAddress}
                onChange={(event) => updateSearch({ laundryAddress: event.target.value })}
                leftIcon={<MapPin size={18} />}
                placeholder="Hotel, apartment, area..."
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 text-base shadow-none"
              />
            </FieldShell>

            <FieldShell label="Pickup date">
              <Input
                type="date"
                value={laundryDate}
                onChange={(event) => updateSearch({ laundryDate: event.target.value })}
                leftIcon={<CalendarDays size={18} />}
                className="h-14 rounded-[1.15rem] border-luxury-dune/80 bg-luxury-pearl/80 shadow-none"
              />
            </FieldShell>

            <SearchButton href="/laundry" />
          </div>
        ) : null}
      </div>
    </div>
  );
}

function FieldShell({
  label,
  children,
  className
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={cn("block space-y-2", className)}>
      <span className="px-1 text-xs font-bold uppercase tracking-[0.15em] text-slate-500">
        {label}
      </span>
      {children}
    </label>
  );
}

function SearchButton({ href }: { href: string }) {
  return (
    <div className="flex items-end">
      <Button asChild variant="gold" size="lg" className="h-14 w-full px-7 shadow-gold xl:w-auto">
        <a href={href}>
          <Search className="mr-2" size={19} />
          Search
        </a>
      </Button>
    </div>
  );
}

export function calculateRentalDays(pickupDate: string, returnDate: string): number {
  if (!pickupDate || !returnDate) return 1;

  const start = new Date(pickupDate);
  const end = new Date(returnDate);

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 1;

  const diff = end.getTime() - start.getTime();
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

  return days > 0 ? days : 1;
}

export function calculateCarRentalTotal(pricePerDay: number, rentalDays: number): number {
  return pricePerDay * rentalDays;
}

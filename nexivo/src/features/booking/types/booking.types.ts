export type BookingSearchState = {
  service: "stays" | "cars" | "laundry";
  destination: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  pickupDate: string;
  returnDate: string;
  pickupLocation: string;
  laundryDate: string;
  laundryAddress: string;
};

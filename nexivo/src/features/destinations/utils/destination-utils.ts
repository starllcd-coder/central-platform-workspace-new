import { destinationExperiences, destinationGuides } from "@/features/destinations/data/destination-guides";

export function getDestinationGuideBySlug(slug: string) {
  return destinationGuides.find((destination) => destination.slug === slug);
}

export function getFeaturedDestinationGuides(limit = 6) {
  return destinationGuides.slice(0, limit);
}

export function getDestinationExperiences(slug: string) {
  return destinationExperiences.filter((experience) => experience.destinationSlug === slug);
}

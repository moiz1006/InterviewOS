import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind classes safely — `clsx` handles conditional classes,
 * `twMerge` resolves conflicts (e.g. `cn("p-2", condition && "p-4")`
 * correctly keeps only `p-4` instead of leaving both). Standard shadcn/ui
 * convention; every component in `components/ui/` uses this instead of
 * template-string concatenation.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

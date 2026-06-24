import {Calendar} from "../api/api-generated-types";

export interface HighlightPart {
  highlighted: boolean;
  text: string;
}

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

export const getSearchTerms = (query: string | undefined): string[] => (
  (query ?? "")
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
);

export const calendarMatchesSearch = (calendar: Calendar, searchTerms: string[]): boolean => {
  if (searchTerms.length === 0) {
    return true;
  }

  const searchableText = [calendar.name, calendar.description, calendar.category, calendar.uid]
    .join(" ")
    .toLowerCase();

  return searchTerms.every((term) => searchableText.includes(term));
};

export const getHighlightParts = (text: string, searchTerms: string[] = []): HighlightPart[] => {
  const terms = Array.from(new Set(searchTerms.filter(Boolean))).sort((a, b) => b.length - a.length);

  if (terms.length === 0) {
    return [{highlighted: false, text}];
  }

  const regex = new RegExp(`(${terms.map(escapeRegExp).join("|")})`, "gi");

  return text.split(regex).map((part) => ({
    highlighted: terms.some((term) => term.toLowerCase() === part.toLowerCase()),
    text: part,
  }));
};

import { Box, Divider, Stack, Text } from "@chakra-ui/react";
import { useMatch, useSearch } from "@tanstack/react-router";
import { useGetSchedule } from "../api";
import { Calendar, Person } from "../api/api-generated-types";
import {calendarMatchesSearch, getSearchTerms} from "../utils/search";
import SearchHighlight from "./searchHighlight";
import SingleCalendar from "./singleCalendar";

type CalendarRowProps = {
  calendar: Calendar;
  persons: Map<string, Person>;
  searchTerms?: string[];
};

const CalendarRow = ({calendar, persons, searchTerms = []}: CalendarRowProps) => (
  <Box key={calendar.uid}>
    <Divider />
    <SingleCalendar
      category={calendar.category}
      calendar={calendar}
      persons={persons}
      searchTerms={searchTerms}
    />
  </Box>
);

type CategoryScheduleProps = {
  calendars: Calendar[];
  category: string;
  persons: Map<string, Person>;
};

const CategorySchedule = ({calendars, category, persons}: CategoryScheduleProps) => (
  <>
    {calendars
      .filter((calendar) => calendar.category == category)
      .map((calendar: Calendar) => (
        <CalendarRow calendar={calendar} key={calendar.uid} persons={persons} />
      ))}
  </>
);

type SearchScheduleProps = {
  calendars: Calendar[];
  categories: string[];
  persons: Map<string, Person>;
  searchQuery: string;
  searchTerms: string[];
};

const SearchSchedule = ({calendars, categories, persons, searchQuery, searchTerms}: SearchScheduleProps) => {
  const shownCalendars = calendars.filter((calendar) => calendarMatchesSearch(calendar, searchTerms));
  const groupedSearchResults = categories
    .map((categoryName) => ({
      calendars: shownCalendars.filter((calendar) => calendar.category === categoryName),
      category: categoryName,
    }))
    .filter((group) => group.calendars.length > 0);

  return (
    <>
      {shownCalendars.length === 0 ? (
        <Text>No duty teams found for &quot;{searchQuery}&quot;.</Text>
      ) : null}
      {groupedSearchResults.map((group) => (
        <Box key={group.category}>
          <Text color="gray.600" fontSize="sm" fontWeight="semibold" mb={2} mt={2}>
            <SearchHighlight searchTerms={searchTerms} text={group.category} />
          </Text>
          {group.calendars.map((calendar: Calendar) => (
            <CalendarRow calendar={calendar} key={calendar.uid} persons={persons} searchTerms={searchTerms} />
          ))}
        </Box>
      ))}
    </>
  );
};

const Schedule = () => {
  const data = useMatch("/$category", { strict: false });
  const search = useSearch({strict: false}) as {search?: string};
  const {
    data: { config, calendars, persons }
  } = useGetSchedule();
  const category = data && data.params && data.params.category !== undefined
    ? decodeURI(data.params.category)
    : config.categories[0];

  const personsMap = new Map(Object.entries(persons));
  const searchQuery = (search.search ?? "").trim();
  const searchTerms = getSearchTerms(search.search);

  // Design heavily influenced by https://chakra-templates.dev/page-sections/pricing
  return (
    <Box py={6} px={5} width={"100%"}>
      <Stack spacing={4} width={"100%"} direction={"column"}>
        {searchQuery ? (
          <SearchSchedule
            calendars={calendars}
            categories={config.categories}
            persons={personsMap}
            searchQuery={searchQuery}
            searchTerms={searchTerms}
          />
        ) : (
          <CategorySchedule calendars={calendars} category={category} persons={personsMap} />
        )}
      </Stack>
    </Box>
  );
};

export default Schedule;

import { Box, Divider, Stack } from "@chakra-ui/react";
import { useMatch } from "@tanstack/react-router";
import { useGetSchedule } from "../api";
import { Calendar } from "../api/api-generated-types";
import SingleCalendar from "./singleCalendar";

const Schedule = () => {
  const data = useMatch("/$category", { strict: false });
  const {
    data: { config, calendars, persons }
  } = useGetSchedule();
  const category = data && data.params && data.params.category !== undefined
    ? decodeURI(data.params.category)
    : config.categories[0];

  const personsMap = new Map(Object.entries(persons));

  // Design heavily influenced by https://chakra-templates.dev/page-sections/pricing
  return (
    <Box py={6} px={5} width={"100%"}>
      <Stack spacing={4} width={"100%"} direction={"column"}>
        {calendars
          .filter((calendar) => calendar.category == category)
          .map((calendar: Calendar, index) => (
            <Box key={index}>
              <Divider />
              <SingleCalendar
                key={"singleCalendarNr" + index}
                category={category}
                calendar={calendar}
                persons={personsMap}
              />
            </Box>
          ))}
      </Stack>
    </Box>
  );
};

export default Schedule;

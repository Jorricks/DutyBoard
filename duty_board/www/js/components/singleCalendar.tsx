import { Box, Button, Heading, List, ListItem, Stack, useColorModeValue } from "@chakra-ui/react";
import { useCollapse } from "react-collapsed";
import { Calendar, Person } from "../api/api-generated-types";
import ExpandedCalendarInfo from "./expandedCalendarInfo";
import { FaCalendarCheck } from "react-icons/fa";
import { FaCalendarTimes } from "react-icons/fa";
import PersonComponent from "./personComponent";
import {useEffect, useState} from "react";
import {Link, useMatch} from "@tanstack/react-router";

interface Props {
  category: string;
  calendar: Calendar;
  persons: Map<string, Person>;
}

// Huge credits to https://blog.logrocket.com/create-collapsible-react-components-react-collapsed/
const SingleCalendar = ({ category, calendar, persons }: Props) => {
  const currentRoute = useMatch("/$category/$calendarId", { strict: false });

  const firstEvent = calendar.events.length > 0 ? calendar.events[0] : undefined;
  const firstPersonUid = firstEvent?.personUid ?? undefined;
  const firstPerson = firstPersonUid ? persons.get(firstPersonUid.toString()) : undefined;

  const [isExpanded, setExpanded] = useState(currentRoute?.params?.calendarId == calendar.uid)
  const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded, duration: 500 });

  const checked = true;
  const colorTextLight = checked ? "white" : "purple.600";
  const bgColorLight = checked ? "purple.400" : "gray.300";

  const colorTextDark = checked ? "white" : "purple.500";
  const bgColorDark = checked ? "purple.400" : "gray.300";

  useEffect(() => {
    setExpanded(currentRoute?.params?.calendarId == calendar.uid)
  }, [currentRoute])

  return (
    <>
      <Stack
        p={3}
        py={3}
        justifyContent={{
          base: "flex-start",
          md: "space-around"
        }}
        direction={{
          base: "column",
          md: "row"
        }}
        alignItems={{ md: "center" }}
      >
        <Box width={{base: "auto", md: "25%"}}>
          <Heading size={"md"}>{calendar.name}</Heading>
        </Box>
        <Box width={{base: "auto", md: "25%"}}>
          <List spacing={3} textAlign="start">
            <ListItem key="def">
              <Box color="green.500" style={{ display: "inline-block" }} mr={3}>
                <FaCalendarCheck />
              </Box>
              <Box style={{ display: "inline-block" }}>{firstEvent?.startEvent ?? "unknown"}</Box>
            </ListItem>
            <ListItem key="abc">
              <Box color="green.500" style={{ display: "inline-block" }} mr={3}>
                <FaCalendarTimes />
              </Box>
              <Box style={{ display: "inline-block" }}>{firstEvent?.endEvent ?? "unknown"}</Box>
            </ListItem>
          </List>
        </Box>
        <Box width={{base: "auto", md: "30%"}}>
          <Heading size={"md"}>
            <div>
              {firstPerson == undefined
                  ? <p>Unknown</p>
                  : <PersonComponent person={firstPerson} />
              }
            </div>
          </Heading>
        </Box>
        <Box width={{base: "auto", md: "10%"}}>
          <Stack>
            <div className="header">
              {isExpanded
                  ? <Link to="/$category" params={{ category: category}}>
                      <Button
                        size="md"
                        color={useColorModeValue(colorTextLight, colorTextDark)}
                        bgColor={useColorModeValue(bgColorLight, bgColorDark)}
                      >
                        Close
                      </Button>
                    </Link>
                  : <Link to="/$category/$calendarId" params={{ category: category, calendarId: calendar.uid }}>
                      <Button
                        size="md"
                        color={useColorModeValue(colorTextLight, colorTextDark)}
                        bgColor={useColorModeValue(bgColorLight, bgColorDark)}
                      >
                        More info
                      </Button>
                    </Link>
              }
            </div>
          </Stack>
        </Box>
      </Stack>
      <div {...getCollapseProps()}>
        <div className="content">
          <ExpandedCalendarInfo calendar={calendar} persons={persons} />
        </div>
      </div>
    </>
  );
};

export default SingleCalendar;

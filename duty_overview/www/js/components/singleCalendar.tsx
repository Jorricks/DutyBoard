import {Box, Button, Heading, List, ListItem, Stack, useColorModeValue} from "@chakra-ui/react";
import useCollapse from "react-collapsed";
import {Calendar, Person} from "../api/api-generated-types";
import ExpandedCalendarInfo from "./expandedCalendarInfo";
import { FaCalendarCheck } from "react-icons/fa";
import { FaCalendarTimes } from "react-icons/fa";
import PersonComponent from "./personComponent";


interface Props {
  calendar: Calendar;
  persons: Map<string, Person>;
}


// Huge credits to https://blog.logrocket.com/create-collapsible-react-components-react-collapsed/
const SingleCalendar = ({
  calendar, persons
}: Props) => {
  const firstEvent = calendar.events.length > 0 ? calendar.events[0] : undefined;
  const firstPersonUid = firstEvent.personUid ?? undefined;
  const firstPerson = firstPersonUid ? persons.get(firstPersonUid.toString()) : undefined;

  const { getCollapseProps, getToggleProps, isExpanded } = useCollapse({duration: 500});


  const checked = true;
  const colorTextLight = checked ? 'white' : 'purple.600';
  const bgColorLight = checked ? 'purple.400' : 'gray.300';

  const colorTextDark = checked ? 'white' : 'purple.500';
  const bgColorDark = checked ? 'purple.400' : 'gray.300';

  return (
    <>
      <Stack
        p={3}
        py={3}
        justifyContent={{
          base: 'flex-start',
          md: 'space-around',
        }}
        direction={{
          base: 'column',
          md: 'row',
        }}
        alignItems={{ md: 'center' }}>
        <Heading size={'md'}>{calendar.name}</Heading>
        <List spacing={3} textAlign="start">
          <ListItem key="def">
            <Box color="green.500" style={{display: "inline-block"}} mr={3}><FaCalendarCheck/></Box>
            <Box style={{display: "inline-block"}}>{firstEvent.startEvent ?? "unknown"}</Box>
          </ListItem>
          <ListItem key="abc">
            <Box color="green.500" style={{display: "inline-block"}} mr={3}><FaCalendarTimes/></Box>
            <Box style={{display: "inline-block"}}>{firstEvent.endEvent ?? "unknown"}</Box>
          </ListItem>
        </List>
        <Heading size={'xl'}>
          <div>
            <PersonComponent person={firstPerson}/>
          </div>
        </Heading>
        <Stack>
          <div className="header" {...getToggleProps()}>
            <Button
              size="md"
              color={useColorModeValue(colorTextLight, colorTextDark)}
              bgColor={useColorModeValue(bgColorLight, bgColorDark)}>
                {isExpanded ? 'Less': 'More'}
            </Button>
          </div>
        </Stack>
      </Stack>
      <div  {...getCollapseProps()}>
        <div className="content">
          <ExpandedCalendarInfo
            calendar={calendar}
            persons={persons}
            />
        </div>
      </div>
    </>
  );
}

export default SingleCalendar;

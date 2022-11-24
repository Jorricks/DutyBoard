import {Button, Heading, List, ListItem, ListIcon, Stack, useColorModeValue,} from "@chakra-ui/react";
import {Calendar, Person} from "../api/api-generated-types";


interface Props {
  calendar: Calendar;
  persons: Map<string, Person>;
}


const SingleCalendar = ({
  calendar, persons
}: Props) => {
  console.log({calendar});
  const firstEvent = calendar.events[0];
  console.log({firstEvent});
  const firstPersonUid = firstEvent.personUid;
  console.log({firstPersonUid});
  console.log({persons});
  const firstPerson = persons.get(firstPersonUid.toString());

  const checked = true;
  const colorTextLight = checked ? 'white' : 'purple.600';
  const bgColorLight = checked ? 'purple.400' : 'gray.300';

  const colorTextDark = checked ? 'white' : 'purple.500';
  const bgColorDark = checked ? 'purple.400' : 'gray.300';

  return (
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
          <ListIcon color="green.500" />
          {firstEvent.startEvent}
        </ListItem>
        <ListItem key="abc">
          <ListIcon color="green.500" />
          {firstEvent.endEvent}
        </ListItem>
      </List>
      <Heading size={'xl'}>{firstPerson.ldap}</Heading>
      <Stack>
        <Button
          size="md"
          color={useColorModeValue(colorTextLight, colorTextDark)}
          bgColor={useColorModeValue(bgColorLight, bgColorDark)}>
          Get Started
        </Button>
      </Stack>
    </Stack>
  );
}

export default SingleCalendar;

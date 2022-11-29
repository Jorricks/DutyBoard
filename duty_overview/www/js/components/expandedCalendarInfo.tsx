import {Divider, TableContainer, Table, Text, Tr, Tbody, Td, Box,} from "@chakra-ui/react";
import {Calendar, Events, Person} from "../api/api-generated-types";
import ParsingError from "./parsingError";
import ParsingWarning from "./parsingWarning";
import PersonComponent from "./personComponent";


interface Props {
  calendar: Calendar;
  persons: Map<string, Person>;
}

const ExpandedCalendarInfo = ({
  calendar, persons
}: Props) => {
  return (
    <Box bg="#f5f5f5">
      <Divider />
      {calendar.errorMsg &&
        <>
          <ParsingError
            errorDescription="Last attempted update of this calendar failed."
            error={calendar.errorMsg}
            />
          <Divider />
        </>
      }

      {!calendar.sync &&
        <>
          <ParsingWarning
            warningMessage={
            "Sync has been disabled for this calendar. Last update was " + calendar.lastUpdate + ". \n" +
              "Soon there might not be events shown here anymore."
          }
          />
          <Divider />
        </>
      }
      <Box p={10}>
        <Box>
          <Text as='b'>Description</Text>
          <Text>{calendar.description}</Text>
        </Box>
        <Box mt={10}>
          <Text as='b'>Schedule</Text>
          <TableContainer>
            <Table variant='simple'>
              {/*<TableCaption>Schedule for {calendar.name}.</TableCaption>*/}
              <Tbody>
                {calendar.events.map((event: Events, index) => (
                  <Tr key={event.personUid + "CalendarUidNr" + calendar.uid + "AndPersonComponentNr" + index}>
                    <Td>{event.startEvent}</Td>
                    <Td>{event.endEvent}</Td>
                    <Td>
                      <PersonComponent person={persons.get(event.personUid.toString())}/>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </TableContainer>
        </Box>
        <Box mt={6}>
          <Text as ='b' style={{display: "inline"}}>Last update was: </Text>
          <Text style={{display: "inline"}}>{calendar.lastUpdate}</Text>
        </Box>
      </Box>
    </Box>
  );
}

export default ExpandedCalendarInfo;

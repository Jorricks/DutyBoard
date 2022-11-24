import { Box, Divider, Stack } from "@chakra-ui/react";
import axios, { AxiosResponse } from "axios";
import { useQuery } from "react-query";
import {useGetSchedule} from "../api";
import {Calendar, CurrentSchedule} from "../api/api-generated-types";
import SingleCalendar from "./single_calendar"
import useErrorToast from "../utils/useErrorToast";

// function Todos() {
//   const { isLoading, isError, data, error } = useQuery('todos', fetchTodoList)
//
//   if (isLoading) {
//     return <span>Loading...</span>
//   }
//
//   if (isError) {
//     return <span>Error: {error.message}</span>
//   }
//
//   // We can assume by this point that `isSuccess === true`
//   return (
//     <ul>
//       {data.map(todo => (
//         <li key={todo.id}>{todo.title}</li>
//       ))}
//     </ul>
//   )
// }


const Schedule = () => {
  const { data: { calendars, persons }, isLoading } = useGetSchedule();
  const personsMap = new Map(Object.entries(persons));

  // Design heavily influenced by https://chakra-templates.dev/page-sections/pricing
  return (
    <Box py={6} px={5} width={'100%'}>
      <Stack spacing={4} width={'100%'} direction={'column'}>
        {calendars.map((calendar: Calendar, index) => (
          <>
            <Divider />
            <SingleCalendar
              key={index}
              calendar={calendar}
              persons={personsMap}
            />
          </>
        ))}
      </Stack>
    </Box>
  )

  // const errorToast = useErrorToast();
  // const abc = "hallo"
  // const { isLoading, isError, data, error } = useQuery(['todos', abc], fetchSchedule);
  // console.log({data, isLoading, isError, error});
  //
  // if (isLoading) {
  //   return <span>Loading...</span>
  // }
  //
  // if (isError) {
  //   errorToast({ error });
  //   return <span>Error: {error.message}</span>
  // }
  //
  // // We can assume by this point that `isSuccess === true`
  // return (
  //   <ul>
  //     {data}
  //   </ul>
  // )
}

export default Schedule;

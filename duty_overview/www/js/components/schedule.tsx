import axios, { AxiosResponse } from "axios";
import { useQuery } from "react-query";
import {useGetSchedule} from "../api";
import {CurrentSchedule} from "../api/api-generated-types";

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

const fetchSchedule = async () => {
  console.log("Fetching");
  const rawData = await axios.get("http://localhost:8080/get_schedule/");
  console.log({rawData});
  return rawData
}

const Schedule = () => {
  const abc = "hallo"
  const { isLoading, isError, data, error } = useQuery(['todos', abc], fetchSchedule);
  console.log({data, isLoading, isError, error});

  if (isLoading) {
    return <span>Loading...</span>
  }

  if (isError) {
    return <span>Error: {error.message}</span>
  }

  // We can assume by this point that `isSuccess === true`
  return (
    <ul>
      {data}
    </ul>
  )
}

export default Schedule;

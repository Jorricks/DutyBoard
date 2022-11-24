import { useQuery } from 'react-query';
import axios, { AxiosResponse } from 'axios';

import useErrorToast from '../utils/useErrorToast';
import {Calendar, CurrentSchedule, Person} from "./api-generated-types";

export const emptyScheduleData: CurrentSchedule = {
  calendars: [],
  persons: {},
};

const useGetSchedule = () => {
  const errorToast = useErrorToast();

  const query = useQuery(
    ['useGetSchedule'],
    async () => {
      return await axios.get<AxiosResponse, CurrentSchedule>("http://localhost:8000/get_schedule/")
    },
    {
      keepPreviousData: true,
      onError: (error: Error) => {
        errorToast({error});
        console.log(error);
      },
    }
  )
  return {
    ...query,
    data: query.data ?? emptyScheduleData,
  };
};

export default useGetSchedule;

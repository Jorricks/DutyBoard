import { useQuery } from 'react-query';
import axios, { AxiosResponse } from 'axios';

import useErrorToast from '../utils/useErrorToast';
import {PersonResponse} from "./api-generated-types";


const useGetSchedule = ({personUid}: {personUid: number}) => {
  const errorToast = useErrorToast();
  const timezoneValue = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const params = {person_uid: personUid, timezone: timezoneValue}
  return useQuery(
    ['useGetSchedule', personUid],
    () => axios.get<AxiosResponse, PersonResponse>("http://localhost:8000/get_person", {params: params}),
    {
      keepPreviousData: true,
      onError: (error: Error) => {
        errorToast({error});
        console.error(error);
      },
    }
  );
};

export default useGetSchedule;

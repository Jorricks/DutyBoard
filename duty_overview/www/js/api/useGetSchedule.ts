import { useQuery } from 'react-query';
import axios, { AxiosResponse } from 'axios';

import useErrorToast from '../utils/useErrorToast';
import {CurrentSchedule} from "./api-generated-types";

const useGetSchedule = () => {
  const errorToast = useErrorToast();

  const query = useQuery(
    ['useGetSchedule'],
    async () => {
      return await axios.get<AxiosResponse, CurrentSchedule>("/get_schedule/")
    },
    {
      onError: (error) => {
        errorToast({error});
        console.log(error);
      },
    }
  )
  return {
    ...query,
    data: query.data,
  };
};

export default useGetSchedule;

import { useQuery } from 'react-query';
import axios, { AxiosResponse } from 'axios';

import useErrorToast from '../utils/useErrorToast';
import type { API } from '.';

const useGetSchedule = () => {
  const errorToast = useErrorToast();

  const query = useQuery(
    ['useGetSchedule'],
    async () => {
      const params = {
        ["timezone"]: "GMT+2",
      };
      return await axios.get<AxiosResponse, API.CurrentSchedule>("/get_schedule/", { params });
    },
    {
      onError: (error: Error) => {
        errorToast({
          title: 'Unable to fetch schedule',
          error,
        });
        throw (error);
      },
    },
  );
  return {
    ...query,
    data: query.data,
  };
};

export default useGetSchedule;

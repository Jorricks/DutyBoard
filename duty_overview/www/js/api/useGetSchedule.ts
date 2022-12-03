import { useQuery } from "react-query";
import axios, { AxiosResponse } from "axios";

import useErrorToast from "../utils/useErrorToast";
import { CurrentSchedule } from "./api-generated-types";

export const emptyScheduleData: CurrentSchedule = {
  config: {
    companyColorHex: "#3C9C2D",
    categories: ["Loading..", "123"]
  },
  calendars: [],
  persons: {}
};

const useGetSchedule = () => {
  const errorToast = useErrorToast();
  const timezoneValue = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const query = useQuery(
    ["useGetSchedule"],
    async () => {
      return await axios.get<AxiosResponse, CurrentSchedule>("http://localhost:8000/get_schedule", {
        params: { timezone: timezoneValue }
      });
    },
    {
      keepPreviousData: true,
      onError: (error: Error) => {
        errorToast({ error });
        console.error(error);
      }
    }
  );
  return {
    ...query,
    data: query.data ?? emptyScheduleData
  };
};

export default useGetSchedule;

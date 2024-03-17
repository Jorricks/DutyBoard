import { useQuery } from "@tanstack/react-query";
import axios, { AxiosResponse } from "axios";

import { CurrentSchedule } from "./api-generated-types";

export const emptyScheduleData: CurrentSchedule = {
  config: {
    categories: ["Loading..", "123"],
    announcements: [],
    timezone: "",
    textColor: "",
    backgroundColor: "",
    gitRepositoryUrl: "",
    enableAdminButton: false,
    announcementTextColor: "",
    announcementBackgroundColor: "",
    footerHtml: ""
  },
  calendars: [],
  persons: {}
};

const useGetSchedule = () => {
  const timezoneValue = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const query = useQuery(
    {
      queryKey: ["useGetSchedule", timezoneValue],
      queryFn: async () => {
        return await axios.get<AxiosResponse, CurrentSchedule>("/schedule", {
          params: { timezone: timezoneValue }
        });
      },
    }
  );
  return {
    ...query,
    data: query.data ?? emptyScheduleData
  };
};

export default useGetSchedule;

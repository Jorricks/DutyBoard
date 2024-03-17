import { useQuery } from "@tanstack/react-query";
import axios, { AxiosResponse } from "axios";

import { PersonResponse } from "./api-generated-types";

const useGetPerson = ({ personUid }: { personUid: number }) => {
  const timezoneValue = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const params = { person_uid: personUid, timezone: timezoneValue };
  return useQuery(
    {
      queryKey: ["useGetPerson", personUid],
      queryFn: async () => {
        return await axios.get<AxiosResponse, PersonResponse>("/person", {
          params: params
        });
      },
    }
  );
};

export default useGetPerson;

import axios, { AxiosResponse } from "axios";
import camelcaseKeys from "camelcase-keys";

import useGetSchedule from "./useGetSchedule";

// const instance = axios.create({
//   baseURL: "http://localhost:8000/",
//   withCredentials: false
// });
if (import.meta.env.VITE_PRODUCTION === "false") {
  axios.defaults.baseURL = import.meta.env.VITE_API_ADDRESS;
}
axios.interceptors.response.use((res: AxiosResponse) =>
  res.data ? camelcaseKeys(res.data, { deep: true }) : res
);
axios.defaults.headers.common.Accept = "application/json";

// export default instance;
export { useGetSchedule };

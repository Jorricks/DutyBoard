import axios, { AxiosResponse } from 'axios';
import camelcaseKeys from 'camelcase-keys';

import useGetSchedule from "./useGetSchedule";

const instance = axios.create({
  baseURL: 'http://localhost:8000/',
  withCredentials: false,
});
axios.interceptors.response.use(
  (res: AxiosResponse) => (res.data ? camelcaseKeys(res.data, { deep: true }) : res),
);
axios.defaults.headers.common.Accept = 'application/json';

export default instance
export { useGetSchedule };

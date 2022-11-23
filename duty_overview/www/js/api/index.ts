import axios from 'axios';
import useGetSchedule from "./useGetSchedule";

const instance = axios.create({
  baseURL: 'http://localhost:5000/',
  withCredentials: false,
});
axios.defaults.headers.common.Accept = 'application/json';

export default instance
export { useGetSchedule };

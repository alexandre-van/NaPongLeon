import axios from 'axios';

const host = window.location.hostname;
const port = window.location.port;

const api = axios.create({
  baseURL: `http://${host}:${port}/api`,
  withCredentials: true
});

api.defaults.timeout = 0;
export default api;

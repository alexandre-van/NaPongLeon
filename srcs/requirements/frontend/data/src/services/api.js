import axios from 'axios';

const host = window.location.hostname;
const port = window.location.port;

const api = axios.create({
  baseURL: `http://${host}:${port}/api`,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

export default api;

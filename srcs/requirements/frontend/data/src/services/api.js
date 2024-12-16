import axios from 'axios';

const protocol = location.protocol;
const host = window.location.hostname;
const port = window.location.port;

function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const api = axios.create({
  baseURL: `${location.origin}/api`,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Request interceptor to add CSRF token to every request
api.interceptors.request.use(function (config) {
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
}, function (error) {
  return Promise.reject(error);
});

// Response interceptor to handle CSRF token updates
api.interceptors.response.use(function (response) {
  const newCsrfToken = response.headers['x-csrftoken'];
  if (newCsrfToken) {
    document.cookie = `csrftoken=${newCsrfToken}; path=/`;
  }
  return response;
}, function (error) {
  return Promise.reject(error);
});

export default api;

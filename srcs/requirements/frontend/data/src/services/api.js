import axios from 'axios';

const protocol = location.protocol;
const host = window.location.hostname;
const port = window.location.port;

let isRefreshing = false;
// For awaiting requests
let failedQueue = [];

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
/*
api.interceptors.response.use(function (response) {
  const newCsrfToken = response.headers['x-csrftoken'];
  if (newCsrfToken) {
    document.cookie = `csrftoken=${newCsrfToken}; path=/`;
  }
  return response;
}, function (error) {
  return Promise.reject(error);
});
*/


api.interceptors.request.use(
  (config) => {
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
      
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    } else {
      console.log('No CSRF token found in cookies');
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const isLoginPage = () => window.location.pathname === '/login';

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 ||
      originalRequest.url === '/authentication/auth/token/refresh/' ||
      originalRequest.url === '/authentication/users/me/' ||
      isLoginPage()) {
        return Promise.reject(error);
    }

    if (!isRefreshing) {
      isRefreshing = true;
      try {
        await api.get('/authentication/auth/token/refresh/');

        failedQueue.forEach(prom => prom.resolve());
        failedQueue = [];

        return api(originalRequest);
      } catch (refreshError) {
        failedQueue.forEach(prom => prom.reject(refreshError));
        failedQueue = [];
        window.location.href = '/login';

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false;
      }
    }

    return new Promise((resolve, reject) => {
      failedQueue.push({ resolve, reject });
    });
  }
);

export default api;

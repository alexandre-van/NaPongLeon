const protocol = location.protocol;
const host = window.location.hostname;
const port = window.location.port;

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `${location.origin}`;
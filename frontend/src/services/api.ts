import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://10.0.2.2:8000', // Android emulator localhost
  // baseURL: 'http://localhost:8000', // iOS simulator
  headers: {
    'Content-Type': 'application/json',
  },
}); 
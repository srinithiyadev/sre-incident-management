import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000/api' });

export const getWorkitems  = ()         => API.get('/workitems');
export const getWorkitem   = (id)       => API.get(`/workitems/${id}`);
export const updateStatus  = (id, s)    => API.patch(`/workitems/${id}/status`, { new_status: s });
export const submitRCA     = (id, data) => API.post(`/workitems/${id}/rca`, data);
export const sendSignal    = (data)     => API.post('/signals', data);
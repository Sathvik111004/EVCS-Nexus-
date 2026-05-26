import axios from 'axios';

// 1. UPDATE THIS LINE: Use 127.0.0.1 instead of localhost
const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllCities = async () => {
  const response = await api.get('/cities/all');
  return response.data;
};

export const classifyCity = async (city) => {
  const response = await api.post('/cities/classify', { city });
  return response.data;
};

export const getRecommendation = async (city, numChargers) => {
  const response = await api.post('/infrastructure/recommend', {
    city,
    num_chargers: numChargers,
  });
  return response.data;
};

export const simulateScenario = async (
  city,
  numChargers,
  chargerCost,
  utilizationHours,
  electricityCost,
  chargingPrice
) => {
  const response = await api.post('/scenario/simulate', {
    city,
    num_chargers: numChargers,
    charger_cost: chargerCost,
    utilization_hours: utilizationHours,
    electricity_cost: electricityCost,
    charging_price: chargingPrice,
  });
  return response.data;
};

export default api;
import axios from 'axios'
// Api service for easier http requests

class ApiService {
  constructor() {
    // Create a client with specified details
    this.client = axios.create({ baseURL: import.meta.env.VITE_API_URL, withCredentials: true })

    // Logs error and propagates it
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error', error.response?.data || error.message)
        return Promise.reject(error)
      },
    )
  }

  get(url, params = {}) {
    return this.client.get(url, { params }).then((res) => res.data)
  }

  post(url, data) {
    return this.client.post(url, data).then((res) => res.data)
  }

  put(url, data) {
    return this.client.put(url, data).then((res) => res.data)
  }

  delete(url) {
    return this.client.delete(url).then((res) => res.data)
  }
}

// Creates a global api service
export const apiService = new ApiService()

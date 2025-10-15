import axios from 'axios'


class ApiService{
    constructor(){
        this.client = axios.create({baseURL: import.meta.env.VITE_API_URL, withCredentials: true});

        this.client.interceptors.response.use(response => response, error =>{
            console.error('API Error', error.response?.data || error.message);
            return Promise.reject(error)
        });
    }

    get(url, params = {}){
        return this.client.get(url, {params}).then(res => res.data);
    }

    post(url, data){
        return this.client.post(url, data).then(res => res.data);    
    }

    put(url, data){
        return this.client.put(url, data).then(res => res.data);
    }

    delete(url){
        return this.client.delete(url).then(res => res.data);
    }
}

export const apiService = new ApiService();
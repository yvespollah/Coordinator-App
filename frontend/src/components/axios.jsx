import axios from 'axios'


const baseUrl = 'http://127.0.0.1:8090/'

const AxiosInstance = axios.create({
    baseURL: baseUrl,
    timeout: 5000, // for latency between the request
    headers:{
        "Content-Type": "application/json",
        accept: "application/json"
    }
})

export default AxiosInstance
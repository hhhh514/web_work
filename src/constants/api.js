import axios from 'axios';
import {ref} from 'vue';
const apiBaseUrl = 'http://localhost:5000';//'http://salanakawaii.tplinkdns.com:5000';
axios.defaults.baseURL = apiBaseUrl;
const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}
axios.defaults.withCredentials = true;
const customerId = ref(localStorage.getItem('userId'));
console.log(customerId)
export {customerId,apiBaseUrl};

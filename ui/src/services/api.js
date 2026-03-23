import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api/v1',
});

export const analyzeChatLog = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/analyze', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getSystemInfo = async () => {
    const response = await api.get('/info');
    return response.data;
};

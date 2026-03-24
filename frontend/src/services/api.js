import axiosClient from '../api/axiosClient';

export const getChatHistory = async () => {
    const response = await axiosClient.get('/chat/history');
    return response.data.messages || [];
};

export const sendChatMessage = async (message) => {
    const response = await axiosClient.post('/chat/', { message });
    return response.data.data.answer;
};

export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axiosClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
};

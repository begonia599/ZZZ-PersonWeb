import { ref } from 'vue';

interface Message {
  text: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

export function useMessage() {
  const message = ref<Message>({ text: '', type: 'info' });

  const showMessage = (text: string, type: Message['type'] = 'success') => {
    message.value = { text, type };
  };

  const clearMessage = () => {
    message.value = { text: '', type: 'info' };
  };

  return {
    message,
    showMessage,
    clearMessage
  };
}
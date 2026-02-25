import { configureStore } from '@reduxjs/toolkit';
import agentsReducer from './slices/agentsSlice';
import conversationsReducer from './slices/conversationsSlice';
import messagesReducer from './slices/messagesSlice';

export const store = configureStore({
  reducer: {
    agents: agentsReducer,
    conversations: conversationsReducer,
    messages: messagesReducer,
  },
  devTools: true,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

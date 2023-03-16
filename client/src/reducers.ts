import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type AuthState = {
  token: string | null;
};

const initialAuthState: AuthState = {
  token: JSON.parse(window.localStorage.getItem("token") || "null"),
};

export const auth = createSlice({
  name: "auth",
  initialState: initialAuthState,
  reducers: {
    setAuth: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
    },
  },
});

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
      window.localStorage.setItem("token", JSON.stringify(action.payload));
    },
    loggedOut: (state) => {
      state.token = null;
      window.localStorage.removeItem("token");
    },
  },
});

export type NotificationLevel = "error" | "warning" | "info";

export type NotificationAction = "reload";

export type NotificationActionDescription = {
  action: NotificationAction;
  display: string;
};

export type Notification = {
  level: NotificationLevel;
  title: string;
  text: string;
  actions: NotificationActionDescription[];
  dt: string;
};

type NotificationState = Notification[];

const initialNotificationState: NotificationState = [];

export const notifications = createSlice({
  name: "notifications",
  initialState: initialNotificationState,
  reducers: {
    notify: (state, action: PayloadAction<Omit<Notification, "dt">>) => {
      const t = new Date();
      const hours = `${t.getHours()}`.padStart(2, "0");
      const mins = `${t.getMinutes()}`.padStart(2, "0");
      const secs = `${t.getSeconds()}`.padStart(2, "0");
      const dt = `${t.getFullYear()}-${
        t.getMonth() + 1
      }-${t.getDate()} ${hours}:${mins}:${secs}`;
      state.unshift({ dt, ...action.payload });
    },
    removeNotification: (state, action: PayloadAction<number>) => {
      state.splice(action.payload, 1);
    },
    action: (_state, action: PayloadAction<NotificationAction>) => {
      switch (action.payload) {
        case "reload":
          window.location.reload();
          break;

        default:
          break;
      }
    },
  },
});

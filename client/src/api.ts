import { createApi, fetchBaseQuery, retry } from "@reduxjs/toolkit/query/react";

import { RootState } from "./store";

declare const SERVICE_URL: string;

export type User = {
  id: number;
  first_name: string;
  last_name: string;
  role: "user" | "admin";
  image: string | null;
};

const baseQuery = retry(
  fetchBaseQuery({
    baseUrl: `${SERVICE_URL}`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  { maxRetries: 6 }
);

export const api = createApi({
  baseQuery,
  endpoints: (builder) => ({
    token: builder.query<string, string>({
      query: (code: string) => ({
        url: "/auth/token",
        method: "POST",
        body: { code },
      }),
      transformResponse: (response: { access_token: string }) =>
        response.access_token,
    }),
    me: builder.query<User, void>({
      query: () => "/auth/me",
    }),
  }),
});

export const { useTokenQuery, useMeQuery } = api;

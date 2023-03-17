import { createApi, fetchBaseQuery, retry } from "@reduxjs/toolkit/query/react";
import type { FetchArgs } from "@reduxjs/toolkit/query";

import { RootState } from "./store";

declare const SERVICE_URL: string;
declare const WEBSOCKET_URL: string;

export type User = {
  id: number;
  first_name: string;
  last_name: string;
  role: "user" | "admin";
  image: string | null;
};

export type PollOption = [text: string, id: number];

export type Poll = {
  id: number;
  title: string;
  description: string;
  options: PollOption[];
  votes: { [id: string]: number };
};

type NewPollMessage = {
  msg: "new_poll";
  id?: number;
  title: string;
  description: string;
  options: Array<[text: string, id?: number]>;
};

type PollVoteMessage = {
  msg: "poll_vote";
  poll: number;
  option: number;
};

type AuthMessage = {
  msg: "auth";
  bearer: string;
};

const authMessage = (token: string): AuthMessage => ({
  msg: "auth",
  bearer: token,
});

type Message = AuthMessage | NewPollMessage | PollVoteMessage;

let socket: WebSocket | null = null;
export const getSocket = (): WebSocket => {
  if (!socket) {
    socket = new WebSocket(`${WEBSOCKET_URL}`);
  }
  return socket;
};

const baseQuery = retry(
  async (args: string | FetchArgs, api, extraOptions) => {
    const result = await fetchBaseQuery({
      baseUrl: `${SERVICE_URL}`,
      prepareHeaders: (headers, { getState }) => {
        const token = (getState() as RootState).auth.token;
        if (token) {
          headers.set("authorization", `Bearer ${token}`);
        }
        return headers;
      },
    })(args, api, extraOptions);

    // bail out of retries if unauthorized
    if (result.error?.status === 403) {
      retry.fail(result.error);
    }

    return result;
  },
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
    polls: builder.query<Poll[], void>({
      query: () => "/poll/",
      async onCacheEntryAdded(
        _arg,
        { cacheDataLoaded, cacheEntryRemoved, updateCachedData }
      ) {
        try {
          await cacheDataLoaded;

          const socket = getSocket();

          socket.addEventListener("message", (event: MessageEvent) => {
            const message: Message = JSON.parse(event.data);
            switch (message.msg) {
              case "auth": {
                socket.send(
                  JSON.stringify(
                    authMessage(
                      JSON.parse(window.localStorage.getItem("token") || "null")
                    )
                  )
                );
                break;
              }
              case "poll_vote": {
                updateCachedData((draft) => {
                  const i = draft.map((poll) => poll.id).indexOf(message.poll);
                  const poll = draft[i];
                  if (poll) {
                    if (poll.votes[message.option]) {
                      poll.votes[message.option]++;
                    }
                  }
                  return draft;
                });
                break;
              }
            }
            console.log(message);
          });

          await cacheEntryRemoved;

          socket.close();
        } catch {
          // if cacheEntryRemoved resolved before cacheDataLoaded,
          // cacheDataLoaded throws
        }
      },
    }),
  }),
});

export const { useTokenQuery, useMeQuery, usePollsQuery } = api;

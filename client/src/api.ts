import { createApi, fetchBaseQuery, retry } from "@reduxjs/toolkit/query/react";
import type { FetchArgs } from "@reduxjs/toolkit/query";
import * as R from "ramda";

import { notifications } from "./reducers";
import { store } from "./store";
import type { RootState } from "./store";

declare const SERVICE_URL: string;
declare const WEBSOCKET_URL: string;

export type User = {
  id: number;
  first_name: string;
  last_name: string;
  role: "user" | "admin";
  image: string | null;
};

export type TokenRequest = {
  code: string;
  redirect: string;
};

export type PollOption = [text: string, id: number];

export type Poll = {
  id: number;
  title: string;
  description: string;
  hidden: boolean;
  options: PollOption[];
  votes: { [id: string]: number };
};

export type Comment = {
  id: number;
  text: string;
  user: string;
};

export type Discussion = {
  id: number;
  text: string;
  votes: number;
  user: string;
  comments: Comment[];
};

type State = {
  polls: Poll[];
  qas: Discussion[];
};

type NewDiscussionMessage = {
  msg: "new_qa";
  id: number;
  text: string;
  user: string;
};

type DiscussionVoteMessage = {
  msg: "qa_vote";
  qa: number;
  count: number;
};

type DiscussionCommentMessage = {
  msg: "qa_comment";
  id: number;
  text: string;
  qa: number;
  user: string;
};

type DeleteDiscussionMessage = {
  msg: "qa_delete";
  qa: number;
};

type NewPollMessage = {
  msg: "new_poll";
  id: number;
  title: string;
  description: string;
  hidden: boolean;
  options: Array<[text: string, id: number]>;
};

type DeletePollMessage = {
  msg: "delete_poll";
  poll_id?: number;
};

type HidePollMessage = {
  msg: "poll_hide";
  poll_id: number;
};

type ShowPollMessage = {
  msg: "poll_show";
  poll_id: number;
};

type PollVoteMessage = {
  msg: "poll_vote";
  poll: number;
  option: number;
  count: number;
};

type AuthMessage = {
  msg: "auth";
  bearer: string;
};

const authMessage = (token: string): AuthMessage => ({
  msg: "auth",
  bearer: token,
});

type Message =
  | AuthMessage
  | NewPollMessage
  | DeletePollMessage
  | PollVoteMessage
  | HidePollMessage
  | ShowPollMessage
  | NewDiscussionMessage
  | DiscussionVoteMessage
  | DiscussionCommentMessage
  | DeleteDiscussionMessage;

let socket: WebSocket | null = null;
export const getSocket = (): WebSocket => {
  if (!socket) {
    socket = new WebSocket(`${WEBSOCKET_URL}`);
    const serverPing = setInterval(
      () => socket?.send(JSON.stringify({ msg: "ping" })),
      10000
    );
    socket.addEventListener("error", (error) => {
      clearInterval(serverPing);
      console.log("Websocket error: ", error);
      store.dispatch(
        notifications.actions.notify({
          level: "error",
          title: "Connection error",
          text: JSON.stringify(error),
          actions: [{ action: "reload", display: "Reload" }],
        })
      );
    });
    socket.addEventListener("close", (event) => {
      clearInterval(serverPing);
      console.log("Websocket closed: ", event);
      store.dispatch(
        notifications.actions.notify({
          level: "error",
          title: "Disconnected",
          text: "You have been disconnected. You should try to reload your browser.",
          actions: [{ action: "reload", display: "Reload" }],
        })
      );
    });
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
    token: builder.query<string, TokenRequest>({
      query: ({ code, redirect }) => ({
        url: "/auth/token",
        method: "POST",
        body: { code, redirect },
      }),
      transformResponse: (response: { access_token: string }) =>
        response.access_token,
    }),
    me: builder.query<User, void>({
      query: () => "/auth/me",
    }),
    state: builder.query<State, void>({
      query: () => "/state/",
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
              case "auth":
                {
                  socket.send(
                    JSON.stringify(
                      authMessage(
                        JSON.parse(
                          window.localStorage.getItem("token") || "null"
                        )
                      )
                    )
                  );
                }
                break;

              case "new_poll":
                {
                  updateCachedData((state) => {
                    state.polls = R.prepend(
                      {
                        id: message.id,
                        title: message.title,
                        description: message.description,
                        hidden: message.hidden,
                        options: message.options,
                        votes: {},
                      },
                      state.polls
                    );
                    return state;
                  });
                }
                break;

              case "delete_poll":
                {
                  if (message.poll_id !== undefined) {
                    updateCachedData((state) => {
                      state.polls = R.filter(
                        (poll: Poll) => poll.id !== message.poll_id,
                        state.polls
                      );
                      return state;
                    });
                  }
                }
                break;

              case "poll_hide":
                {
                  updateCachedData((draft) => {
                    const i = draft.polls
                      .map((poll) => poll.id)
                      .indexOf(message.poll_id);
                    const poll = draft.polls[i];
                    if (poll !== undefined) {
                      poll.hidden = true;
                    }
                    return draft;
                  });
                }
                break;

              case "poll_show":
                {
                  updateCachedData((draft) => {
                    const i = draft.polls
                      .map((poll) => poll.id)
                      .indexOf(message.poll_id);
                    const poll = draft.polls[i];
                    if (poll !== undefined) {
                      poll.hidden = false;
                    }
                    return draft;
                  });
                }
                break;

              case "poll_vote":
                {
                  updateCachedData((draft) => {
                    const i = draft.polls
                      .map((poll) => poll.id)
                      .indexOf(message.poll);
                    const poll = draft.polls[i];
                    if (poll !== undefined) {
                      poll.votes[message.option] = message.count;
                    }
                    return draft;
                  });
                }
                break;

              case "new_qa":
                {
                  updateCachedData((state) => {
                    state.qas = R.prepend(
                      {
                        id: message.id,
                        text: message.text,
                        user: message.user,
                        votes: 0,
                        comments: [],
                      },
                      state.qas
                    );
                    return state;
                  });
                }
                break;

              case "qa_vote":
                {
                  updateCachedData((state) => {
                    if (message.qa !== undefined) {
                      const i = state.qas
                        .map((qa) => qa.id)
                        .indexOf(message.qa);
                      const qa = state.qas[i];
                      if (qa !== undefined) {
                        qa.votes = message.count;
                      }
                    }
                    return state;
                  });
                }
                break;

              case "qa_comment":
                {
                  updateCachedData((state) => {
                    const i = state.qas.map((qa) => qa.id).indexOf(message.qa);
                    const qa = state.qas[i];
                    qa?.comments.unshift({
                      id: message.id,
                      text: message.text,
                      user: message.user,
                    });
                  });
                }
                break;

              case "qa_delete":
                {
                  updateCachedData((state) => {
                    state.qas = R.filter(
                      (qa: Discussion) => qa.id !== message.qa,
                      state.qas
                    );
                    return state;
                  });
                }
                break;
            }
            console.log(message);
          });

          socket.addEventListener("open", () => {
            socket.send(JSON.stringify({ msg: "ready" }));
          });

          await cacheEntryRemoved;

          console.log("Cache entry being removed. Closing the websocket");
          socket.close();
        } catch {
          // if cacheEntryRemoved resolved before cacheDataLoaded,
          // cacheDataLoaded throws
        }
      },
    }),
  }),
});

export const { useTokenQuery, useMeQuery, useStateQuery } = api;

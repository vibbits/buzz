import React from "react";

import { getSocket, Poll, usePollsQuery } from "./api";
import { useAppSelector } from "./store";
import { Welcome } from "./Welcome";
import { Poll as ViewPoll } from "./Poll";

const PollApp: React.FC<{}> = () => {
  const { data } = usePollsQuery();

  const socket = getSocket();

  const select = (poll: number) => (option: number) => () => {
    socket.send(
      JSON.stringify({
        msg: "poll_vote",
        poll,
        option,
      })
    );
  };

  return (
    <div style={{ flex: "1", textAlign: "center" }}>
      <h2>Polls</h2>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          margin: "15px 0",
        }}
      >
        {data?.map((poll: Poll) => (
          <ViewPoll
            key={poll.id}
            title={poll.title}
            description={poll.description}
            options={poll.options}
            votes={poll.votes}
            selectOption={select(poll.id)}
          />
        ))}
      </div>
    </div>
  );
};

const QAApp: React.FC<{}> = () => {
  return (
    <div style={{ flex: "1", textAlign: "center" }}>
      <h2>Q&A</h2>
    </div>
  );
};

export const Buzz: React.FC<{}> = () => {
  const isAuthorized: boolean = useAppSelector(
    (state) => state.auth.token !== null
  );

  if (!isAuthorized) {
    return <Welcome />;
  }
  return (
    <section
      style={{
        display: "flex",
        flexDirection: "row",
        flex: "1",
        minHeight: "600px",
        gap: "6px",
      }}
    >
      <PollApp />
      <div style={{ width: "2px", background: "#ccc" }}></div>
      <QAApp />
    </section>
  );
};

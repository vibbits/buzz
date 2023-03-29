import React, { useState } from "react";

import * as R from "ramda";

import { getSocket, Discussion, Poll, useMeQuery, useStateQuery } from "./api";
import { useAppSelector } from "./store";
import { Welcome } from "./Welcome";
import { Poll as ViewPoll } from "./Poll";
import { ButtonTab } from "./ButtonTab";
import "./Buzz.css";

const selectPollOption = (poll: number) => (option: number) => () => {
  const socket = getSocket();
  socket.send(
    JSON.stringify({
      msg: "poll_vote",
      poll,
      option,
    })
  );
};

const createPoll = (title: string, description: string, options: string[]) => {
  const socket = getSocket();
  socket.send(JSON.stringify({ msg: "new_poll", title, description, options }));
};

const deletePoll = (poll_id: number) => {
  const socket = getSocket();
  socket.send(JSON.stringify({ msg: "delete_poll", poll_id }));
};

const createQA = (text: string) => {
  const socket = getSocket();
  socket.send(JSON.stringify({ msg: "new_qa", text }));
};

type CreatePollOptionProps = {
  index: number;
  option: string | null;
  big: boolean;
  add: () => void;
  set: (index: number, value: string | null) => void;
  remove: (index: number) => void;
};

const CreatePollOption: React.FC<CreatePollOptionProps> = (props) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "3px",
        alignItems: "start",
      }}
    >
      <label htmlFor={`option-${props.index}`}>
        Poll option {`${props.index + 1}`}
      </label>
      <input
        id={`create-option-${props.index}`}
        type="text"
        placeholder={`Option ${props.index + 1}`}
        value={props.option === null ? "" : props.option}
        onChange={(e) =>
          props.set(props.index, e.target.value === "" ? null : e.target.value)
        }
      />
      {props.big ? (
        <button
          className="flat-ui-button"
          style={{ color: "red" }}
          onClick={() => props.remove(props.index)}
        >
          Remove option
        </button>
      ) : null}
    </div>
  );
};

type CreatePollOptionsProps = {
  options: (string | null)[];
  modify: React.Dispatch<React.SetStateAction<(string | null)[]>>;
};

const CreatePollOptions: React.FC<CreatePollOptionsProps> = ({
  options,
  modify,
}) => {
  const remove = (index: number) => {
    modify(R.remove(index, 1));
  };

  const setValue = (index: number, value: string | null) => {
    modify(R.adjust<string | null>(index, R.always(value)));
  };

  const add = () => {
    modify(R.append<string | null>(null));
  };

  return (
    <div>
      {options.map((option, i) => (
        <CreatePollOption
          key={`option-${i}`}
          index={i}
          option={option}
          big={options.length > 2}
          add={add}
          set={setValue}
          remove={remove}
        />
      ))}
      <button onClick={add}>Add option</button>
    </div>
  );
};

const CreatePollButton: React.FC<{}> = () => {
  const [pressed, setPressed] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [options, setOptions] = useState<Array<string | null>>([null, null]);

  if (pressed) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <input
          type="text"
          placeholder="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          type="text"
          placeholder="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <CreatePollOptions options={options} modify={setOptions} />
        <div>
          <button onClick={() => setPressed(false)}>Cancel</button>
          <button
            onClick={() => {
              setPressed(false);
              createPoll(
                title,
                description,
                options.filter((o) => o !== null) as string[]
              );
            }}
          >
            Create Poll
          </button>
        </div>
      </div>
    );
  }

  return <button onClick={() => setPressed(true)}>Create Poll</button>;
};

const DeletePollButton: React.FC<{ pollID: number }> = ({ pollID }) => {
  const { data } = useMeQuery();

  if (data && data.role === "admin") {
    return (
      <button
        className="flat-ui-button"
        style={{ position: "absolute", right: "0" }}
        onClick={() => deletePoll(pollID)}
      >
        ❌
      </button>
    );
  }

  return null;
};

const PollApp: React.FC<{ cn: string }> = ({ cn }) => {
  const { data } = useStateQuery();
  const me = useMeQuery();

  return (
    <section className={`app-container ${cn}`}>
      <h2 className="hide-on-mobile">Polls</h2>
      {me?.data?.role === "admin" ? <CreatePollButton /> : null}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          margin: "15px 0",
        }}
      >
        {data?.polls.map((poll: Poll) => (
          <ViewPoll
            key={poll.id}
            title={poll.title}
            description={poll.description}
            options={poll.options}
            votes={poll.votes}
            selectOption={selectPollOption(poll.id)}
          >
            <DeletePollButton pollID={poll.id} />
          </ViewPoll>
        ))}
      </div>
    </section>
  );
};

const CreateDiscussionButton: React.FC<{}> = () => {
  const [pressed, setPressed] = useState(false);
  const [text, setText] = useState("");

  if (pressed) {
    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <textarea
          rows={15}
          cols={40}
          onChange={(e) => setText(e.target.value)}
        ></textarea>
        <button onClick={() => setPressed(false)}>Cancel</button>
        <button
          onClick={() => {
            setPressed(false);
            createQA(text);
          }}
        >
          Create post
        </button>
      </div>
    );
  }

  return <button onClick={() => setPressed(true)}>Create Poll</button>;
};

const ViewDiscussion: React.FC<{ text: string }> = ({ text }) => {
  return <div className="interaction-box">{text}</div>;
};

const QAApp: React.FC<{ cn: string }> = ({ cn }) => {
  const { data } = useStateQuery();

  return (
    <section className={`app-container ${cn}`}>
      <h2 className="hide-on-mobile">Q&A</h2>
      <CreateDiscussionButton />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          margin: "15px 0",
        }}
      >
        {data?.qas.map((qa: Discussion) => (
          <ViewDiscussion key={qa.id} text={qa.text} />
        ))}
      </div>
    </section>
  );
};

export default () => {
  const [whichApp, setWhichApp] = useState<"poll" | "qa">("poll");
  const isAuthorized: boolean = useAppSelector(
    (state) => state.auth.token !== null
  );

  if (!isAuthorized) {
    return <Welcome />;
  }
  return (
    <div className="buzz-ui-container">
      <ButtonTab app={whichApp} change={setWhichApp} />
      <PollApp cn={whichApp !== "poll" ? "hide-on-mobile" : ""} />
      <div style={{ width: "2px", background: "#ccc" }}></div>
      <QAApp cn={whichApp !== "qa" ? "hide-on-mobile" : ""} />
    </div>
  );
};

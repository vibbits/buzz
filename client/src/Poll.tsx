import React from "react";
import * as R from "ramda";

import { PollOption } from "./api";
import "./Buzz.css";
import "./Poll.css";

type PollProps = {
  title: string;
  description: string;
  options: PollOption[];
  votes: { [id: string]: number };
  selectOption: (_option: number) => () => void;
};

export const Poll: React.FC<React.PropsWithChildren<PollProps>> = (props) => {
  const maxVotes: number = R.values(props.votes).reduce(
    (a: number, b: number): number => Math.max(a, b),
    0
  );

  return (
    <div
      className="interaction-box"
      style={{
        paddingRight: "15px",
        paddingBottom: "15px",
      }}
    >
      {props.children}
      <h3>{props.title}</h3>
      <p>{props.description}</p>
      <ul style={{ textAlign: "left", listStyle: "none" }}>
        {props.options.map((option: PollOption) => {
          const numVotes = props.votes[option[1]];
          return (
            <ViewPollOption
              key={option[1]}
              label={option[0]}
              size={
                numVotes === undefined || maxVotes === 0
                  ? 0
                  : numVotes / maxVotes
              }
              count={numVotes === undefined ? 0 : numVotes}
              selectOption={props.selectOption(option[1])}
            />
          );
        })}
      </ul>
    </div>
  );
};

type PollOptionProps = {
  label: string;
  size: number;
  count: number;
  selectOption: () => void;
};

const ViewPollOption: React.FC<PollOptionProps> = (props) => {
  return (
    <li className="poll-button" onClick={() => props.selectOption()}>
      <p>{props.label}</p>
      <div
        style={{
          height: "22px",
          border: "1px solid #ccc",
          borderRadius: "5px",
        }}
      >
        <div
          className="background-blue"
          style={{
            textAlign: "center",
            width: `${props.size * 100}%`,
            height: "22px",
            color: "white",
            fontSize: "16px",
            lineHeight: "20px",
            borderRadius: "5px",
          }}
        >
          {props.count}
        </div>
      </div>
    </li>
  );
};

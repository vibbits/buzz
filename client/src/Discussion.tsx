import React from "react";

import { Comment } from "./api";
import "./Buzz.css";

type DiscussionProps = {
  user: string;
  text: string;
  votes: number;
  comments: Comment[];
};

type CommentProps = {
  text: string;
  user: string;
};

const Comment: React.FC<CommentProps> = ({ text, user }) => {
  return (
    <div>
      <pre>{text}</pre>
      <p>{user}</p>
    </div>
  );
};

const Votes: React.FC<{ votes: number }> = ({ votes }) => {
  return (
    <div className="votes-box">
      <button className="flat-ui-button">🗩</button>
      {votes}
      <button className="flat-ui-button">👍</button>
    </div>
  );
};

export const Discussion: React.FC<DiscussionProps> = ({
  user,
  text,
  votes,
  comments,
}) => {
  return (
    <div className="interaction-box discussion-box">
      <pre className="discussion-text">{text}</pre>
      <div style={{ margin: "auto 0", textAlign: "start" }}>{user}</div>
      <Votes votes={votes} />
      {comments.length > 0 ? <hr className="subtle-hr" /> : null}
      {comments.map((comment) => (
        <Comment key={comment.id} text={comment.text} user={comment.user} />
      ))}
    </div>
  );
};

import React, { useState } from "react";

import { Comment } from "./api";
import "./Buzz.css";

type DiscussionProps = {
  user: string;
  text: string;
  votes: number;
  comments: Comment[];
  vote: () => void;
  comment: (text: string) => void;
};

type CommentProps = {
  text: string;
  user: string;
};

const Comment: React.FC<CommentProps> = ({ text, user }) => {
  return (
    <div className="comment-container">
      <span className="comment-author">{user}</span>
      <div className="comment">
        <pre>{text}</pre>
      </div>
    </div>
  );
};

const Votes: React.FC<{ votes: number; vote: () => void }> = ({
  votes,
  vote,
}) => {
  return (
    <div className="votes-box">
      {votes}
      <button className="flat-ui-button" onClick={vote}>
        👍
      </button>
    </div>
  );
};

const CommentForm: React.FC<{ comment: (text: string) => void }> = ({
  comment,
}) => {
  const [text, setText] = useState("");

  const submitForm = () => {
    comment(text);
    setText("");
  };

  return (
    <div className="comment-form">
      <textarea
        onChange={(e) => setText(e.target.value)}
        value={text}
      ></textarea>
      <button className="flat-ui-button" onClick={submitForm}>
        Comment
      </button>
    </div>
  );
};

type CommentsViewProps = {
  comments: Comment[];
};

const CommentsView: React.FC<CommentsViewProps> = ({ comments }) => {
  return (
    <div className="comment-view">
      <hr className="subtle-hr" />
      {comments.map((comment) => (
        <Comment key={comment.id} text={comment.text} user={comment.user} />
      ))}
    </div>
  );
};

export const Discussion: React.FC<DiscussionProps> = ({
  user,
  text,
  votes,
  comments,
  vote,
  comment,
}) => {
  return (
    <div className="interaction-box discussion-box">
      <pre className="discussion-text">{text}</pre>
      <div style={{ margin: "auto 0", textAlign: "start" }}>{user}</div>
      <Votes votes={votes} vote={vote} />
      <CommentForm comment={comment} />
      <CommentsView comments={comments} />
    </div>
  );
};

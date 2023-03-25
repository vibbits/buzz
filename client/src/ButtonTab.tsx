import React from "react";

import "./Buzz.css";

export type ButtonTabProps = {
  app: "poll" | "qa";
  change: React.Dispatch<React.SetStateAction<"poll" | "qa">>;
};

export const ButtonTab: React.FC<ButtonTabProps> = ({ app, change }) => {
  return (
    <div className="buttons-container hide-on-desktop">
      <button
        disabled={app === "poll"}
        className={`flat-ui-button ${
          app === "poll"
            ? "button-enabled"
            : "button-disabled inset-shadow-right"
        }`}
        onClick={() => change("poll")}
      >
        <h2>Polls</h2>
      </button>
      <button
        disabled={app === "qa"}
        className={`flat-ui-button ${
          app === "qa" ? "button-enabled" : "button-disabled inset-shadow-left"
        }`}
        onClick={() => change("qa")}
      >
        <h2>Q&A</h2>
      </button>
    </div>
  );
};

import React from "react";

import VIBLogo from "./vib.svg";
import WelcomeImage from "./welcome.svg";

declare const SERVICE_URL: string;

export const Welcome: React.FC<{}> = () => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "15px",
        maxWidth: "600px",
        width: "100%",
      }}
    >
      <img style={{ maxHeight: "55px" }} src={VIBLogo} />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          border: "1px solid #ccc",
          borderRadius: "8px",
          alignItems: "center",
          gap: "15px",
        }}
      >
        <img style={{ borderRadius: "8px 8px 0 0" }} src={WelcomeImage} />
        <a
          href={`${SERVICE_URL}/auth/login`}
          className="background-cyan"
          style={{
            marginBottom: "15px",
            textDecoration: "none",
            width: "120px",
            height: "40px",
            border: "1px solid #42b7ba",
            borderRadius: "2px",
            textAlign: "center",
            lineHeight: "39px",
            fontWeight: "400",
            color: "white",
          }}
        >
          Login
        </a>
      </div>
    </div>
  );
};

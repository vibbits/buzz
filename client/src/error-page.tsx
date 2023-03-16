import React from "react";
import { useRouteError } from "react-router-dom";

export const ErrorPage: React.FC<{}> = () => {
  const error = useRouteError() as { statusText?: string; message?: string };

  return (
    <div id="error-page">
      <h1>Oops!</h1>
      <p>Sorry, an unexpected error has occured.</p>
      <p>
        <i>{error.statusText || error.message}</i>
      </p>
    </div>
  );
};

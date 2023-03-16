import React from "react";

import { useAppSelector } from "./store";
import { Welcome } from "./Welcome";

export const Buzz: React.FC<{}> = () => {
  const isAuthorized: boolean = useAppSelector(
    (state) => state.auth.token !== null
  );

  if (!isAuthorized) {
    return <Welcome />;
  }
  return <div>Buzz!</div>;
};

import React, { useEffect } from "react";
import { Navigate, useSearchParams } from "react-router-dom";

import { useMeQuery, useTokenQuery } from "./api";
import { auth } from "./reducers";
import { useAppDispatch, useAppSelector } from "./store";

declare const SERVICE_URL: string;

export type LoginProps = {
  loggedin: (token: string) => void;
  access_token: string | null;
};

export const LoginRedirect: React.FC<{}> = () => {
  const [searchParams] = useSearchParams();
  const dispatch = useAppDispatch();

  const [authToken] = useAppSelector((state) => [state.auth.token]);

  const code = searchParams.get("code");
  const { data } = useTokenQuery({
    code: code!,
    redirect: `${window.location.origin}/login_redirect`,
  });

  useEffect(() => {
    if (!data) return;

    dispatch(auth.actions.setAuth(data));
  }, [dispatch, data]);

  if (authToken) {
    return <Navigate to="/" />;
  } else {
    return <></>;
  }
};

const UserAuthenticatedButtons: React.FC<{}> = () => {
  const dispatch = useAppDispatch();
  const { data, error } = useMeQuery();

  useEffect(() => {
    if (error) {
      dispatch(auth.actions.loggedOut());
    }
  }, [error]);

  if (data) {
    return (
      <div className="vib-auth">
        {data.role === "admin" ? (
          <a className="vib-auth-button vib-admin">Access Admin</a>
        ) : (
          <></>
        )}
        <a className="vib-auth-button vib-user-info">
          {data.first_name} {data.last_name}
        </a>
      </div>
    );
  } else {
    return (
      <div className="vib-auth">
        <a className="vib-auth-button vib-user-info"></a>
      </div>
    );
  }
};

export const AuthButtons: React.FC<{}> = () => {
  const [authToken] = useAppSelector((state) => [state.auth.token]);

  if (authToken) {
    return <UserAuthenticatedButtons />;
  } else {
    return (
      <div className="vib-auth">
        <a
          className="vib-auth-button"
          href={`${SERVICE_URL}/auth/login?redirect=${window.location.origin}/login_redirect`}
        >
          Login
        </a>
      </div>
    );
  }
};

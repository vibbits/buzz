import React from "react";

import { useAppDispatch, useAppSelector } from "./store";
import { notifications as notify } from "./reducers";
import type {
  NotificationActionDescription,
  NotificationLevel,
} from "./reducers";

import "./Buzz.css";

type NotificationProps = {
  close: () => void;
  level: NotificationLevel;
  title: string;
  message: string;
  time: string;
  actions: NotificationActionDescription[] | undefined;
};

const Notification: React.FC<NotificationProps> = (props) => {
  const dispatch = useAppDispatch();

  return (
    <div className={`notification notification-${props.level}`}>
      <div className="notification-header">
        <span className="notification-title">{props.title}</span>
        <span className="notification-time">{props.time}</span>
      </div>
      <p>{props.message}</p>
      <div className="notification-actions">
        <button onClick={props.close}>Ignore</button>
        {props.actions?.map((a, i) => (
          <button
            key={i}
            onClick={() => dispatch(notify.actions.action(a.action))}
          >
            {a.display}
          </button>
        ))}
      </div>
    </div>
  );
};

export const Notifications: React.FC<{}> = () => {
  const notifications = useAppSelector((state) => state.notifications);
  const dispatch = useAppDispatch();

  return (
    <div className="notify-bar">
      {notifications.map((n, i) => (
        <Notification
          key={i}
          close={() => dispatch(notify.actions.removeNotification(i))}
          level={n.level}
          title={n.title}
          message={n.text}
          time={n.dt}
          actions={n.actions}
        />
      ))}
    </div>
  );
};

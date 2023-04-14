import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import {
  createBrowserRouter,
  Link,
  RouterProvider,
  Outlet,
} from "react-router-dom";
import { Provider } from "react-redux";

import { store } from "./store";
import { ErrorPage } from "./error-page";
import { AuthButtons, LoginRedirect } from "./auth";
const Buzz = React.lazy(() => import("./Buzz"));

import "@vibbioinfocore/vib-css";
import Logo from "./buzz.svg";

const AppHeader = () => {
  return (
    <header className="vib-header">
      <div className="vib-bar-breadcrumb">
        <div className="vib-breadcrumbs">
          <a
            className="vib-main-site"
            href="https://vib.be"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              className="vib-logo-small"
              src="https://vibbits.github.io/vib-css/images/vib.svg"
              alt="VIB Logo"
            />
          </a>
          <Link className="breadcrumb" to="/">
            Buzz @ VIB Technology Training
          </Link>
        </div>
        <AuthButtons />
      </div>
      <nav className="vib-nav">
        <img
          className="vib-app-logo"
          src={Logo}
          alt="Buzz Logo"
          style={{ width: "68px", height: "90px" }}
        />

        <input type="checkbox" id="vib-toggle-menu" />
        <label className="vib-menu-toggle-button" htmlFor="vib-toggle-menu">
          <span className="vib-menu-button-bar vib-menu-top" />
          <span className="vib-menu-button-bar vib-menu-middle" />
          <span className="vib-menu-button-bar vib-menu-bottom" />
        </label>
        <ul className="vib-main-menu" role="menu">
          <li>
            <Link to={`about`}>About</Link>
          </li>
          <li>
            <Link to={`contact`}>Contact</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

const AppFooter = () => {
  return (
    <footer className="vib-main-footer">
      <div className="footer-l" />
      <div className="footer-r">
        <h3>About</h3>
        <div>
          © <a href="https://vib.be">VIB</a> Technology Training 2023.
        </div>
        <div style={{ marginTop: "2rem" }}>Buzz @ VIB Technology Training</div>
      </div>
    </footer>
  );
};

const App: React.FC<{}> = () => {
  useEffect(() => {
    if (!document.body.classList.contains("vib-body")) {
      document.body.classList.add("vib-body");
    }
  });

  return (
    <>
      <AppHeader />
      <main className="vib-main">
        <Outlet />
      </main>
      <AppFooter />
    </>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "/",
        element: (
          <React.Suspense fallback={<>loading...</>}>
            <Buzz />
          </React.Suspense>
        ),
      },
    ],
  },
  {
    path: "/login_redirect",
    element: <LoginRedirect />,
    errorElement: <ErrorPage />,
  },
]);

const root = document.querySelector("#app");
if (root) {
  const app = createRoot(root);
  app.render(
    <React.StrictMode>
      <Provider store={store}>
        <RouterProvider router={router} />
      </Provider>
    </React.StrictMode>
  );
} else {
  console.error("Could not find root element");
}

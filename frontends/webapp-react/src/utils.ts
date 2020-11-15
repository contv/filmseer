import React from "react";
import state from "src/app/states";
import { URLSearchParams } from "url";

type RequestMethodType =
  | "GET"
  | "POST"
  | "PUT"
  | "DELETE"
  | "PATCH"
  | "OPTIONS"
  | "HEAD"
  | "CONNECT"
  | "TRACE";

type ApiParamType = {
  path?: string;
  method?: RequestMethodType;
  params?: { [key: string]: any } | URLSearchParams;
  body?: { [key: string]: any };
};

type WrapperExceptionType = { code: number; message: string };

type WrapperType = {
  status: number;
  code: number;
  message: string;
  exceptions?: WrapperExceptionType[];
  data: { [key: string]: any };
};

class ApiError extends Error {
  status: number;
  code: number;
  exceptions: WrapperExceptionType[];
  data: { [key: string]: any };

  constructor({
    message = "",
    status = 500,
    code = 1000,
    exceptions = [],
    data = {},
  }: {
    message?: string;
    status?: number;
    code?: number;
    exceptions?: WrapperExceptionType[];
    data?: { [key: string]: any };
  } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.exceptions = exceptions;
    this.data = data;
  }
}

const baseUrl = (
  ((document.getElementsByTagName("base")[0] || {}).href || "") + "/"
).replace(/(?<=\/)\/+$/, "");

const baseApiUrl = (
  ((process.env || {}).REACT_APP_API_BASEURL || baseUrl + "api/v1") + "/"
).replace(/(?<=\/)\/+$/, "");

const api = (
  { path, method, params, body }: ApiParamType = { path: "/", method: "GET" }
) => {
  if (!(params instanceof URLSearchParams)) {
    params = Object.assign({}, params);
  }
  if (body instanceof URLSearchParams) {
    params = body;
    body = {};
  }
  if (typeof params === "object" && !(params instanceof URLSearchParams)) {
    Object.keys(params).forEach(
      (key) =>
        params &&
        !(params instanceof URLSearchParams) &&
        (params[key] === undefined || params[key] === null) &&
        delete params[key]
    );
  }
  if (typeof body === "object") {
    Object.keys(body).forEach(
      (key) => body && body[key] === undefined && delete body[key]
    );
  }
  if (
    !body ||
    (typeof body === "object" &&
      Object.keys(body).length === 0 &&
      body.constructor === Object)
  ) {
    body = undefined;
  }
  if (
    !params ||
    (typeof params === "object" &&
      Object.keys(params).length === 0 &&
      params.constructor === Object)
  ) {
    params = undefined;
  }

  method = method || "GET";
  path = path || "/";

  if (
    ["GET", "DELETE", "TRACE", "OPTIONS", "HEAD"].includes(method) &&
    body &&
    typeof body === "object" &&
    Object.keys(body).length > 0
  ) {
    throw TypeError(
      "This method should not have a body, consider using `params` instead."
    );
  }

  return fetch(
    baseApiUrl.replace(/\/+$/, "") +
      path +
      (!params
        ? ""
        : (path.includes("?") ? (path.endsWith("?") ? "" : "&") : "?") +
          (params instanceof URLSearchParams
            ? params.toString()
            : Object.entries(params)
                .map(
                  ([key, val]) =>
                    `${encodeURIComponent(key)}=${encodeURIComponent(val)}`
                )
                .join("&"))),
    {
      method: method,
      cache: "no-store",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow",
      keepalive: true,
      referrerPolicy: "no-referrer-when-downgrade",
      body:
        !body || (Object.keys(body).length === 0 && body.constructor === Object)
          ? undefined
          : JSON.stringify(body),
    }
  )
    .then((response) =>
      response.json().then(async (wrapper) => {
        if (typeof wrapper !== "object") {
          throw TypeError("Incorrect response body");
        }
        return Object.assign({}, wrapper, { status: response.status });
      })
    )
    .then(async (wrapper: WrapperType) => {
      if (
        typeof wrapper.code !== "number" ||
        typeof wrapper.message !== "string" ||
        typeof wrapper.data !== "object"
      ) {
        throw TypeError("Incorrect response body");
      }
      wrapper.code = Math.round(wrapper.code);
      if (wrapper.code !== 0) {
        throw new ApiError({
          message: wrapper.message,
          code: wrapper.code,
          status: wrapper.status,
          data: wrapper.data,
          exceptions: wrapper.exceptions || [],
        });
      }
      return Object.assign({}, wrapper, {
        exceptions: wrapper.exceptions || [],
      });
    });
};

const apiEffect = (
  apiParams: ApiParamType,
  onsuccess: (wrapper: WrapperType) => void,
  onerror: (error: ApiError) => void = (_error) => undefined,
  precondition: () => boolean | Promise<boolean> = () => true
) => {
  return () => {
    let didCancel = false;

    async function fetchApi() {
      let wrapper;
      try {
        wrapper = await api(apiParams);
      } catch (error) {
        if (error instanceof ApiError) {
          if (!didCancel) {
            onerror(error);
          }
        } else {
          throw error;
        }
      }
      if (!didCancel && typeof wrapper !== "undefined") {
        onsuccess(wrapper);
      }
    }

    Promise.resolve(precondition()).then((result) => {
      if (!!result && !didCancel) {
        fetchApi();
      }
    });
    return () => {
      didCancel = true;
    };
  };
};

const usePrevious: <T>(value: T) => T | null = (value) => {
  const ref = React.useRef<typeof value | null>(null);
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

const useIsMounted = () => {
  const isMounted = React.useRef(false);

  React.useEffect(function setIsMounted() {
    isMounted.current = true;

    return function cleanupSetIsMounted() {
      isMounted.current = false;
    };
  }, []);

  return isMounted;
};

const useUpdateEffect: typeof React.useEffect = function useUpdateEffect(
  effect: React.EffectCallback,
  dependencies?: React.DependencyList
) {
  const isMounted = useIsMounted();
  const isInitialMount = React.useRef(true);

  React.useEffect(() => {
    let effectCleanupFunc = function noop() {};

    if (isInitialMount.current) {
      isInitialMount.current = false;
    } else {
      effectCleanupFunc = effect() || effectCleanupFunc;
    }
    return () => {
      effectCleanupFunc();
      if (!isMounted.current) {
        isInitialMount.current = true;
      }
    };
  }, dependencies); // eslint-disable-line react-hooks/exhaustive-deps
};

const notify = (
  text: React.ReactNode,
  level: "warning" | "error" | "info" = "info"
) => {
  for (let i = 0; i < state.notifications.length; i++) {
    if (
      state.notifications[i] &&
      (state.notifications[i] || {}).text === text &&
      (state.notifications[i] || {}).level === level &&
      !(state.notifications[i] || {}).expired
    ) {
      // Prevent infinite re-rendering
      return;
    }
  }
  let notification = {
    id: Date.now() * 1000 + Math.floor(Math.random() * 1000),
    text: text,
    time: Date.now(),
    level: level,
    timeoutHandler: 0,
    expired: false,
  };
  notification.timeoutHandler = window.setTimeout(() => {
    notification.expired = true;
    window.setTimeout(() => {
      for (let i = 0; i < state.notifications.length; i++) {
        if (
          state.notifications[i] &&
          (state.notifications[i] || {}).id === notification.id
        ) {
          state.notifications[i] = null;
        }
      }
    }, 2000);
  }, 2000);
  state.notifications.push(notification);
};

export {
  api,
  apiEffect,
  ApiError,
  usePrevious,
  useUpdateEffect,
  baseUrl,
  baseApiUrl,
  notify,
};

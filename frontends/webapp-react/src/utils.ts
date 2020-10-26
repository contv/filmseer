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
  params?: object;
  body?: object;
};

type WrapperExceptionType = { code: number; message: string };

type WrapperType = {
  status: number;
  code: number;
  message: string;
  exceptions?: WrapperExceptionType[];
  data: object;
};

class ApiError extends Error {
  status: number;
  code: number;
  exceptions: WrapperExceptionType[];
  data: object;

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
    data?: object;
  } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.exceptions = exceptions;
    this.data = data;
  }
}

const api = (
  { path, method, params, body }: ApiParamType = { path: "/", method: "GET" }
) => {
  console.log("before", body);
  if (params instanceof URLSearchParams) {
    params = Object.fromEntries(params);
  } else {
    params = Object.assign({}, params);
  }
  if (body instanceof URLSearchParams) {
    params = Object.assign({}, params, Object.fromEntries(body));
    body = {};
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
    ((process.env || {}).REACT_APP_API_BASEURL || "http://localhost:8000/api/v1") +
      path +
      (!params
        ? ""
        : (path.includes("?") ? (path.endsWith("?") ? "" : "&") : "?") +
          Object.entries(params)
            .map(
              ([key, val]) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(val)}`
            )
            .join("&")),
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
        (!body || (Object.keys(body).length === 0 && body.constructor === Object))
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
  precondition: () => (boolean | Promise<boolean>) = () => true
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
      if (!!result) {
        fetchApi();
      }
    });
    return () => {
      didCancel = true;
    };
  };
};

export { api, apiEffect, ApiError };

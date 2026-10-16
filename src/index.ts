import { Container, getContainer } from "@cloudflare/containers";

// The Python (FastAPI) engine runs inside the container; this Worker only routes requests to it.
export class TvbtContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
}

interface Env {
  TVBT: DurableObjectNamespace<TvbtContainer>;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // The API is stateless and nothing is stored, so one shared instance is enough.
    return getContainer(env.TVBT, "main").fetch(request);
  },
};

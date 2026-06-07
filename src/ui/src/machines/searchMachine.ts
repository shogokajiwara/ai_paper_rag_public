import { setup, assign, fromPromise, fromCallback } from "xstate";

const API_URL = "http://localhost:8000";

export const searchMachine = setup({
  types: {
    context: {} as {
      query: string;
      warning: string;
      data: any;
      jobId: string | null;
      abortController: AbortController | null;
      ws: WebSocket | null;
    },
    events: {} as
      | { type: "SEARCH"; query: string }
      | { type: "WARNING"; message: string }
      | { type: "WS_RESULT"; data: any }
      | { type: "error"; data: any }
  },

  actors: {
    connectWS: fromCallback(({ self, sendBack }) => {
      let ws: WebSocket | null = null;
    
      function connect() {
        ws = new WebSocket("ws://localhost:8000/ws");
    
        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data);
    
          // 結果メッセージだけ machine に送る
          if (msg.type === "result") {
            sendBack({
              type: "WS_RESULT",
              data: msg
            });
          }
        };
      }
    
      connect();
    
      return () => {
        ws?.close();
      };
    }),
    fetchJobId: fromPromise(async ({ input }) => {
      const ctx = input.getCtx();
      const res = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: ctx.query }),
        signal: ctx.abortController?.signal
      });
      return res.json();
    }),
    startJob: fromPromise(async ({ input }) => {
      const ctx = input.getCtx();
      return fetch(`${API_URL}/start-job`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jobId: ctx.jobId,
          query: ctx.query
        })
      });
    })
  }
}).createMachine({
  id: "search",

  context: {
    query: "",
    warning: "",
    data: null,
    jobId: null,
    abortController: null,
    ws: null
  },

  invoke: {
    src: "connectWS"
  },  

  initial: "idle",

  states: {
    idle: {
      on: {
        WARNING: {
          target: "idle",
          actions: assign(({ event }) => ({
            warning: event.message ?? "Please enter your question or topic."
          }))
        },

        SEARCH: {
          target: "requestingJobId",
          actions: assign(({ event }) => ({
            query: event.query,
            data: null,
            warning: ""
          }))
        }
      }
    },

    requestingJobId: {
      entry: assign(() => ({
        abortController: new AbortController()
      })),

      invoke: {
        src: "fetchJobId",
        input: ({ context }) => ({
          getCtx: () => context
        }),

        onDone: {
          target: "startingJob",
          actions: assign(({ event }) => ({
            jobId: event.output.jobId
          }))
        },

        onError: {
          target: "idle",
          actions: assign(() => ({
            data: null,
            warning: "",
            jobId: null
          }))
        }        
      }
    },

    startingJob: {
      invoke: {
        src: "startJob",
        input: ({ context }) => ({
          getCtx: () => context
        }),

        onDone: "waitingResult",

        onError: {
          target: "idle",
          actions: assign(() => ({
            data: null,
            warning: "",
            jobId: null
          }))
        }        
      }
    },

    waitingResult: {
      on: {
        WS_RESULT: {
          guard: ({ context, event }) => event.data.jobId === context.jobId,
          target: "idle",
          actions: assign(({ event }) => ({
            data: event.data,
            jobId: null
          }))
        },
        error: {
          target: "idle",
          actions: assign(({ event }) => ({
            data: null,
            warning: "",
            jobId: null
          }))
        }
      }
    }
  }
});

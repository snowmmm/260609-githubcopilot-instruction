import express from "express";
import { createServer } from "http";
import { WebSocketServer, WebSocket } from "ws";
import cors from "cors";
import { CopilotClient, approveAll } from "@github/copilot-sdk";

const app = express();
app.use(cors());
app.use(express.json());

const server = createServer(app);
const wss = new WebSocketServer({ server });

// Health check endpoint
app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

wss.on("connection", async (ws: WebSocket) => {
  console.log("Client connected");

  let client: CopilotClient | null = null;
  let session: Awaited<ReturnType<CopilotClient["createSession"]>> | null = null;

  try {
    // Create CopilotClient
    client = new CopilotClient();
    await client.start();

    // Create session (model configurable via MODEL env var, default: gpt-5-mini)
    const model = process.env.MODEL || "gpt-5-mini";
    session = await client.createSession({
      model,
      onPermissionRequest: approveAll,
      streaming: true,
    });

    console.log(`Session created: ${session.sessionId}`);
    ws.send(JSON.stringify({ type: "connected", sessionId: session.sessionId }));

    // Set up streaming event handlers
    session.on("assistant.message_delta", (event) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: "delta",
          content: event.data.deltaContent,
        }));
      }
    });

    session.on("assistant.message", (event) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: "message",
          content: event.data.content,
        }));
      }
    });

    session.on("session.idle", () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "idle" }));
      }
    });

  } catch (error) {
    console.error("Failed to initialize Copilot session:", error);
    ws.send(JSON.stringify({ type: "error", message: "Failed to initialize Copilot session" }));
    ws.close();
    return;
  }

  // Handle incoming messages
  ws.on("message", async (data: Buffer) => {
    try {
      const msg = JSON.parse(data.toString());

      if (msg.type === "chat" && msg.content && session) {
        console.log(`User: ${msg.content}`);
        await session.send({ prompt: msg.content });
      }
    } catch (error) {
      console.error("Error processing message:", error);
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "error", message: "Failed to process message" }));
      }
    }
  });

  // Handle disconnect
  ws.on("close", async () => {
    console.log("Client disconnected");
    try {
      if (session) await session.disconnect();
      if (client) await client.stop();
    } catch (e) {
      console.error("Error cleaning up:", e);
    }
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

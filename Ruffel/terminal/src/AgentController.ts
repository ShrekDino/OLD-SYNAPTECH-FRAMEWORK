import { readFileSync } from "fs"
import { resolve } from "path"
import { JsonRpcTransport, JsonRpcNotification } from "./JsonRpcTransport"

export type SessionStatus = {
  sessionId: string
  turnCount: number
  messageCount: number
  totalTokensUsed: number
  status: string
}

export type PermissionRequest = {
  requestId: string
  toolName: string
  summary: string
}

export type QuestionRequest = {
  question: string
  requestId: string
}

export type UndoResult = {
  success: boolean
  count: number
  reverted: string[]
  error?: string
}

export type AgentEvent =
  | { type: "notification"; method: string; params: Record<string, unknown> }
  | { type: "permission"; request: PermissionRequest }
  | { type: "question"; request: QuestionRequest }
  | { type: "connected" }
  | { type: "disconnected"; error?: string }

export class AgentController {
  private transport: JsonRpcTransport
  private sessionId = ""
  private eventHandlers = new Set<(event: AgentEvent) => void>()
  private workDir: string

  constructor(private binaryPath: string, workDir: string) {
    this.workDir = workDir
    this.transport = new JsonRpcTransport({
      binaryPath,
      args: ["--rpc", "--dir", workDir],
    })
    this.transport.onNotification((n: JsonRpcNotification) => this.handleNotification(n))
  }

  onEvent(handler: (event: AgentEvent) => void): () => void {
    this.eventHandlers.add(handler)
    return () => this.eventHandlers.delete(handler)
  }

  private emit(event: AgentEvent): void {
    this.eventHandlers.forEach((h) => h(event))
  }

  async start(): Promise<void> {
    const memoryContent = this.readMemoryFile()

    await this.transport.start()

    const params: Record<string, unknown> = {
      working_directory: this.workDir,
    }
    if (memoryContent) {
      params.seed_context = memoryContent
    }

    const result = await this.transport.request<{ session_id: string; model: string; status: string }>("session/start", params)
    this.sessionId = result.session_id
    this.emit({ type: "connected" })
  }

  async sendInput(text: string): Promise<void> {
    await this.transport.request("input/send", { text })
  }

  async undoLastAction(count = 1): Promise<UndoResult> {
    return this.transport.request<UndoResult>("session/undo", { count })
  }

  async respondPermission(requestId: string, response: string): Promise<void> {
    await this.transport.request("permission/respond", { request_id: requestId, response })
  }

  async respondQuestion(answer: string): Promise<void> {
    await this.transport.request("permission/respond", { request_id: "question", response: answer })
  }

  cancel(): void {
    this.transport.cancel()
  }

  async stop(): Promise<void> {
    this.emit({ type: "disconnected" })
    await this.transport.stop()
  }

  private handleNotification(n: JsonRpcNotification): void {
    const params = (n.params ?? {}) as Record<string, unknown>
    this.emit({ type: "notification", method: n.method, params })

    switch (n.method) {
      case "permission/ask": {
        this.emit({
          type: "permission",
          request: {
            requestId: params.call_id as string,
            toolName: params.tool_name as string,
            summary: params.summary as string,
          },
        })
        break
      }
      case "question/ask": {
        this.emit({
          type: "question",
          request: {
            question: params.question as string,
            requestId: params.call_id as string,
          },
        })
        break
      }
    }
  }

  private readMemoryFile(): string | undefined {
    const candidates = [
      resolve(this.workDir, ".opencode", "MEMORY.md"),
      resolve(this.workDir, ".openmono", "MEMORY.md"),
      resolve(this.workDir, "MEMORY.md"),
    ]

    for (const filePath of candidates) {
      try {
        const content = readFileSync(filePath, "utf-8").trim()
        if (content) return content
      } catch {
        // file doesn't exist, try next
      }
    }
    return undefined
  }
}

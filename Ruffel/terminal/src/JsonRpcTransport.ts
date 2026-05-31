import { ChildProcess, spawn } from "child_process"

export type JsonRpcNotification = {
  method: string
  params?: Record<string, unknown>
}

export type NotificationHandler = (notification: JsonRpcNotification) => void

export class JsonRpcTransport {
  private process: ChildProcess | null = null
  private pending = new Map<string | number, { resolve: (v: unknown) => void; reject: (e: Error) => void; timer: NodeJS.Timeout }>()
  private nextId = 1
  private notificationHandlers = new Set<NotificationHandler>()

  // Byte-level stream buffers
  private stdoutBuffer = Buffer.alloc(0)
  private stderrChunks: string[] = []

  private binaryPath: string
  private args: string[]

  constructor(opts: {
    binaryPath: string
    args?: string[]
  }) {
    this.binaryPath = opts.binaryPath
    this.args = opts.args ?? ["--rpc"]
  }

  get stderrLog(): string {
    return this.stderrChunks.join("")
  }

  async start(timeoutMs = 10000): Promise<void> {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("Timeout starting openmono process")), timeoutMs)

      this.process = spawn(this.binaryPath, this.args, {
        stdio: ["pipe", "pipe", "pipe"],
      })

      this.process.stdout?.on("data", (chunk: Buffer) => {
        this.stdoutBuffer = Buffer.concat([this.stdoutBuffer, chunk])
        this.flushStdoutBuffer()
      })

      this.process.stderr?.on("data", (chunk: Buffer) => {
        this.stderrChunks.push(chunk.toString("utf-8"))
      })

      this.process.on("exit", (code) => {
        this.rejectAllPending(new Error(`Process exited with code ${code}`))
      })

      this.process.on("error", (err) => {
        clearTimeout(timer)
        reject(err)
      })

      this.process.on("spawn", () => {
        clearTimeout(timer)
        resolve()
      })
    })
  }

  private flushStdoutBuffer(): void {
    while (true) {
      const nl = this.stdoutBuffer.indexOf(10)
      if (nl === -1) break

      const line = this.stdoutBuffer.subarray(0, nl).toString("utf-8").trim()
      this.stdoutBuffer = this.stdoutBuffer.subarray(nl + 1)

      if (!line) continue

      try {
        const msg = JSON.parse(line)
        if ("method" in msg && typeof msg.method === "string") {
          this.notificationHandlers.forEach((h) => h(msg as JsonRpcNotification))
        } else if ("id" in msg) {
          const pending = this.pending.get(msg.id)
          if (pending) {
            clearTimeout(pending.timer)
            this.pending.delete(msg.id)
            if (msg.error) pending.reject(new Error(msg.error.message))
            else pending.resolve(msg.result)
          }
        }
      } catch {
        // Non-JSON line on stdout is forwarded to stderr context
        this.stderrChunks.push(`[stdout parse error] ${line}\n`)
      }
    }
  }

  async request<R = unknown>(method: string, params?: Record<string, unknown>, timeoutMs = 30000): Promise<R> {
    const id = this.nextId++
    const msg = JSON.stringify({ jsonrpc: "2.0", id, method, params })

    return new Promise<R>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`Request ${method} timed out after ${timeoutMs}ms`))
      }, timeoutMs)

      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject, timer })
      this.process?.stdin?.write(msg + "\n")
    })
  }

  onNotification(handler: NotificationHandler): () => void {
    this.notificationHandlers.add(handler)
    return () => this.notificationHandlers.delete(handler)
  }

  cancel(): void {
    this.request("input/cancel", {}, 2000).catch(() => {})
  }

  private rejectAllPending(error: Error) {
    for (const [id, pending] of this.pending) {
      clearTimeout(pending.timer)
      pending.reject(error)
      this.pending.delete(id)
    }
  }

  async stop(): Promise<void> {
    try {
      await this.request("session/stop", {}, 2000)
    } catch { /* ignore */ }

    if (this.process) {
      this.process.kill("SIGTERM")
      await new Promise((r) => setTimeout(r, 500))
      if (this.process.exitCode === null) {
        this.process.kill("SIGKILL")
      }
    }

    this.process = null
  }
}

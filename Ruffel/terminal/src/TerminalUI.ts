import * as readline from "readline"
import { AgentController, PermissionRequest, QuestionRequest, UndoResult } from "./AgentController"

const ESC = "\x1b"
const BOLD = `${ESC}[1m`
const DIM = `${ESC}[2m`
const GREEN = `${ESC}[32m`
const YELLOW = `${ESC}[33m`
const RED = `${ESC}[31m`
const CYAN = `${ESC}[36m`
const RESET = `${ESC}[0m`
const ERASE_LINE = `${ESC}[2K\r`
const SAVE_CURSOR = `${ESC}s`
const RESTORE_CURSOR = `${ESC}u`

export class TerminalUI {
  private rl: readline.Interface
  private controller: AgentController
  private pendingPermission: PermissionRequest | null = null
  private pendingQuestion: QuestionRequest | null = null
  private inputSuspended = false
  private currentLine = ""
  private running = true
  private turnActive = false

  constructor(controller: AgentController) {
    this.controller = controller
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: `${CYAN}ruffel>${RESET} `,
    })
  }

  async run(): Promise<void> {
    this.controller.onEvent((event) => {
      switch (event.type) {
        case "connected":
          this.printLine(`${GREEN}✓${RESET} Ruffel Mono Agent session started`)
          this.printLine(`${DIM}Type a message, or /help for commands${RESET}`)
          this.resumeInput()
          break
        case "disconnected":
          this.printLine(`${YELLOW}Session ended${RESET}`)
          this.running = false
          this.rl.close()
          break
        case "notification":
          this.handleNotification(event.method, event.params)
          break
        case "permission":
          this.handlePermission(event.request)
          break
        case "question":
          this.handleQuestion(event.request)
          break
      }
    })

    this.rl.on("line", async (line) => {
      if (this.inputSuspended) return

      const trimmed = line.trim()
      if (!trimmed) {
        this.rl.prompt()
        return
      }

      if (trimmed === "/exit" || trimmed === "/quit") {
        await this.controller.stop()
        return
      }

      if (trimmed === "/undo") {
        const result = await this.controller.undoLastAction()
        this.renderUndoResult(result)
        this.rl.prompt()
        return
      }

      if (trimmed === "/help") {
        this.printLine(`${CYAN}Commands:${RESET}`)
        this.printLine(`  /undo    Undo last agent action`)
        this.printLine(`  /exit    Exit the agent`)
        this.printLine(`  /help    Show this help`)
        this.rl.prompt()
        return
      }

      this.turnActive = true
      try {
        await this.controller.sendInput(trimmed)
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err)
        this.printLine(`${RED}Error:${RESET} ${msg}`)
      }
      this.turnActive = false
      this.rl.prompt()
    })

    this.rl.on("close", () => {
      this.running = false
    })

    // Ctrl+C handling
    this.rl.on("SIGINT", () => {
      if (this.turnActive) {
        this.printLine(`${YELLOW}Cancelling...${RESET}`)
        this.controller.cancel()
      } else {
        this.controller.stop().then(() => this.rl.close())
      }
    })

    // Show initial prompt
    this.rl.prompt()

    // Wait until running stops
    await new Promise<void>((resolve) => {
      const check = setInterval(() => {
        if (!this.running) {
          clearInterval(check)
          resolve()
        }
      }, 100)
    })
  }

  private handleNotification(method: string, params: Record<string, unknown>): void {
    switch (method) {
      case "text/delta":
        this.streamText(params.delta as string)
        break
      case "turn/start":
        this.printLine("")
        break
      case "turn/end":
        this.printLine("")
        break
      case "text/thinking":
        this.printLine(`${DIM}${params.delta as string}${RESET}`)
        break
      case "text/thinking_collapsed":
        this.printLine(`${DIM}[thinking collapsed: ${String(params.char_count ?? "")} chars]${RESET}`)
        break
      case "text/markdown":
        this.printLine(params.content as string)
        break
      case "text/diff":
        this.printLine(`${DIM}${params.content as string}${RESET}`)
        break
      case "text/tool_content": {
        const p = params
        this.printLine(`${DIM}[${p.tool_name as string}] ${p.file_path as string}${RESET}`)
        break
      }
      case "tool/start": {
        const p = params
        this.printLine(`${DIM}→ ${p.tool_name as string}: ${p.arguments as string}${RESET}`)
        break
      }
      case "tool/result": {
        const p = params
        if (p.success) {
          this.printLine(`${DIM}✓ ${p.tool_name as string} succeeded${RESET}`)
        } else {
          this.printLine(`${RED}✗ ${p.tool_name as string} failed${RESET}${p.error ? `: ${p.error as string}` : ""}`)
        }
        break
      }
      case "tool/crash": {
        const p = params
        this.printLine(`${RED}✗ ${p.tool_name as string} crashed: ${p.error as string}${RESET}`)
        break
      }
      case "session/welcome": {
        const p = params
        this.printLine(`${GREEN}Ruffel Mono Agent${RESET}`)
        this.printLine(`${DIM}Model: ${p.model as string} | ${p.endpoint as string}${RESET}`)
        break
      }
      case "session/error": {
        this.printLine(`${RED}${params.message as string}${RESET}`)
        break
      }
      case "session/warning": {
        this.printLine(`${YELLOW}${params.content as string}${RESET}`)
        break
      }
      case "session/info": {
        this.printLine(`${DIM}${params.content as string}${RESET}`)
        break
      }
      case "session/debug": {
        this.printLine(`${DIM}[debug] ${params.content as string}${RESET}`)
        break
      }
      case "session/clear":
        console.clear()
        break
      case "session/waiting":
        this.printLine(`${DIM}...${RESET}`)
        break
      case "session/todos":
        // Could render todos inline; skip for now
        break
    }
  }

  private handlePermission(request: PermissionRequest): void {
    this.pendingPermission = request
    this.suspendInput()

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    })

    this.printLine("")
    this.printLine(`${YELLOW}Permission required for ${request.toolName}:${RESET}`)
    this.printLine(`${DIM}${request.summary}${RESET}`)

    rl.question(`${GREEN}[a]llow / [d]eny / allow [A]ll / deny [D]ll? ${RESET}`, async (answer: string) => {
      const cmd = answer.trim().toLowerCase()
      const response = cmd === "a" || cmd === "allow" ? "allow"
        : cmd === "A" || cmd === "all" || cmd === "always" ? "allow_all"
        : cmd === "D" || cmd === "deny_all" || cmd === "never" ? "deny_all"
        : "deny"
      await this.controller.respondPermission(request.requestId, response)
      rl.close()
      this.pendingPermission = null
      this.resumeInput()
    })
  }

  private handleQuestion(request: QuestionRequest): void {
    this.pendingQuestion = request
    this.suspendInput()

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    })

    this.printLine("")
    this.printLine(`${CYAN}${request.question}${RESET}`)

    rl.question(`${GREEN}Answer:${RESET} `, async (answer: string) => {
      await this.controller.respondQuestion(answer.trim())
      rl.close()
      this.pendingQuestion = null
      this.resumeInput()
    })
  }

  private streamText(text: string): void {
    if (text) {
      process.stdout.write(text)
    }
  }

  private printLine(text: string): void {
    // Save cursor position, clear current input line, print message, restore
    if (this.inputSuspended) {
      process.stdout.write(text + "\n")
    } else {
      const currentInput = this.currentLine
      process.stdout.write(ERASE_LINE + text + "\n")
      this.rl.prompt()
    }
  }

  private suspendInput(): void {
    this.inputSuspended = true
    this.rl.pause()
  }

  private resumeInput(): void {
    this.inputSuspended = false
    this.rl.resume()
    this.rl.prompt()
  }

  private renderUndoResult(result: UndoResult): void {
    if (result.success) {
      this.printLine(`${GREEN}Undone ${result.count} actions:${RESET}`)
      for (const file of result.reverted) {
        this.printLine(`  ${file}`)
      }
    } else {
      this.printLine(`${YELLOW}Undo failed: ${result.error || "unknown"}${RESET}`)
    }
  }
}

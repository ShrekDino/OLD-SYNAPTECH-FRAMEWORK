import { AgentController } from "./AgentController"
import { TerminalUI } from "./TerminalUI"

export async function main(args: string[]): Promise<void> {
  let binaryPath = "openmono"
  let workDir = process.cwd()

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    const next = i + 1 < args.length ? args[i + 1] : null

    switch (arg) {
      case "--binary":
      case "-b":
        if (next) { binaryPath = next; i++ }
        break
      case "--dir":
      case "-d":
        if (next) { workDir = next; i++ }
        break
      case "--help":
      case "-h":
        console.log("Ruffel Mono Agent — Terminal Client")
        console.log("")
        console.log("Usage: ruffel [options]")
        console.log("")
        console.log("Options:")
        console.log("  --binary, -b <path>  Path to openmono binary (default: openmono)")
        console.log("  --dir, -d <path>     Working directory (default: current dir)")
        console.log("  --help, -h           Show this help")
        process.exit(0)
    }
  }

  const controller = new AgentController(binaryPath, workDir)
  const ui = new TerminalUI(controller)

  try {
    await controller.start()
    await ui.run()
  } finally {
    await controller.stop()
  }
}

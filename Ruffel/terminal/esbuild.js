import * as esbuild from "esbuild"

const isWatch = process.argv.includes("--watch")

const config = {
  entryPoints: ["src/index.ts"],
  outfile: "dist/index.js",
  bundle: true,
  platform: "node",
  target: "node20",
  format: "esm",
  sourcemap: false,
  minify: false,
}

if (isWatch) {
  const ctx = await esbuild.context(config)
  await ctx.watch()
  console.log("[watch] build started")
} else {
  await esbuild.build(config)
  console.log("[build] dist/index.js")
}

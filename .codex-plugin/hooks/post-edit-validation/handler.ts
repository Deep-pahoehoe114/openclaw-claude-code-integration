import { spawnSync } from "node:child_process";

const result = spawnSync("python3", ["tools/post_edit_validate.py"], {
  stdio: "inherit",
});

process.exit(result.status ?? 1);

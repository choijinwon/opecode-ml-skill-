import { access, appendFile, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { join } from "node:path";

const WELCOME_GUIDE_MESSAGE = [
  "GenAI - MLflow - AI Studio 적용을 돕는 OpenCode 패키지입니다.",
  "중점 기능: Prompt, Tracking/Trace, Chat Session, Judge, Dataset",
  "모델 프로젝트 경로를 알려주면 AI Studio 적용 관점으로 분석할 수 있습니다.",
  "API key, password, token 값은 출력하지 않습니다.",
  "다시 보려면 채팅에서 /launch 를 입력하세요.",
].join("\n");

async function exists(path) {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function log(directory, message) {
  const logFile = join(directory, ".opencode", "welcome-guide.log");
  await appendFile(logFile, `${new Date().toISOString()} ${message}\n`, "utf-8").catch(() => {});
}

async function showWelcomeOnce({ client, directory }, reason = "startup") {
  const seenFile = join(directory, ".opencode", ".welcome_guide_seen");
  if (await exists(seenFile)) return;

  try {
    await client.tui.showToast({
      body: {
        variant: "info",
        title: "Launch Guide",
        message: WELCOME_GUIDE_MESSAGE,
        duration: 30000,
      },
      query: {
        directory,
      },
    });
    await writeFile(seenFile, new Date().toISOString(), "utf-8");
    await log(directory, `shown reason=${reason}`);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    await log(directory, `failed reason=${reason} error=${detail}`);
  }
}

export default {
  id: "shiftone-welcome-guide",
  async server(input) {
    setTimeout(() => showWelcomeOnce(input, "startup-delay"), 2500);
    return {
      async event({ event }) {
        if (event.type === "server.connected") {
          await showWelcomeOnce(input, "server.connected");
        }
        if (event.type === "session.created") {
          await showWelcomeOnce(input, "session.created");
        }
      },
    };
  },
};

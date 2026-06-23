import { access, writeFile } from "node:fs/promises";
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

async function showWelcomeOnce({ client, directory }) {
  const seenFile = join(directory, ".opencode", ".welcome_guide_seen");
  if (await exists(seenFile)) return;

  setTimeout(async () => {
    try {
      await client.tui.showToast({
        body: {
          variant: "info",
          title: "Launch Guide",
          message: WELCOME_GUIDE_MESSAGE,
          duration: 30000,
        },
      });
      await writeFile(seenFile, new Date().toISOString(), "utf-8");
    } catch {
      // TUI may not be ready in headless/debug modes. Avoid breaking OpenCode startup.
    }
  }, 1200);
}

export default {
  id: "shiftone-welcome-guide",
  async server(input) {
    await showWelcomeOnce(input);
    return {};
  },
};

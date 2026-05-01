const readline = require("readline");

function renderPrompt(options, selected, index) {
  const lines = [
    "Selecione as IDEs (setas para mover, espaço para marcar, enter para confirmar):",
    "",
  ];

  for (let cursor = 0; cursor < options.length; cursor += 1) {
    const prefix = cursor === index ? ">" : " ";
    const mark = selected.has(options[cursor]) ? "[x]" : "[ ]";
    lines.push(`${prefix} ${mark} ${options[cursor]}`);
  }

  lines.push("");
  lines.push("Selecione pelo menos uma IDE.");
  return lines.join("\n");
}

function clearScreen() {
  process.stdout.write("\u001Bc");
}

async function promptMultiSelect(options) {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    throw new Error("A seleção interativa requer um terminal TTY. Use --ides para modo não interativo.");
  }

  readline.emitKeypressEvents(process.stdin);
  const previousRawMode = process.stdin.isRaw;
  if (typeof process.stdin.setRawMode === "function") {
    process.stdin.setRawMode(true);
  }

  const selected = new Set(options);
  let index = 0;

  return new Promise((resolve, reject) => {
    const onKeypress = (_, key) => {
      if (!key) {
        return;
      }

      if (key.name === "up") {
        index = index === 0 ? options.length - 1 : index - 1;
        clearScreen();
        process.stdout.write(renderPrompt(options, selected, index));
        return;
      }

      if (key.name === "down") {
        index = index === options.length - 1 ? 0 : index + 1;
        clearScreen();
        process.stdout.write(renderPrompt(options, selected, index));
        return;
      }

      if (key.name === "space") {
        const value = options[index];
        if (selected.has(value)) {
          selected.delete(value);
        } else {
          selected.add(value);
        }
        clearScreen();
        process.stdout.write(renderPrompt(options, selected, index));
        return;
      }

      if (key.name === "return") {
        if (selected.size === 0) {
          return;
        }
        cleanup();
        resolve([...selected]);
        return;
      }

      if ((key.ctrl && key.name === "c") || key.name === "escape") {
        cleanup();
        reject(new Error("Seleção cancelada."));
      }
    };

    const cleanup = () => {
      process.stdin.off("keypress", onKeypress);
      if (typeof process.stdin.setRawMode === "function") {
        process.stdin.setRawMode(Boolean(previousRawMode));
      }
      process.stdout.write("\n");
    };

    clearScreen();
    process.stdout.write(renderPrompt(options, selected, index));
    process.stdin.on("keypress", onKeypress);
  });
}

module.exports = {
  promptMultiSelect,
};

export function filenameSlug(value) {
  const slug = value
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
  return slug || "scientific-applet";
}

function csvCell(value) {
  const text = String(value ?? "");
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function csvFromRows(columns, rows) {
  const header = columns.map((column) => csvCell(column.label)).join(",");
  const records = rows.map((row) => {
    return columns.map((column) => csvCell(row[column.key])).join(",");
  });
  return [header, ...records].join("\r\n") + "\r\n";
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function dataUrlToBlob(dataUrl) {
  const [metadata, encoded] = dataUrl.split(",", 2);
  const mime =
    metadata.match(/^data:([^;]+);base64$/)?.[1] ||
    "application/octet-stream";
  const bytes = Uint8Array.from(atob(encoded), (character) =>
    character.charCodeAt(0),
  );
  return new Blob([bytes], { type: mime });
}

function canvasBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error("The browser could not create a PNG."));
      }
    }, "image/png");
  });
}

function loadImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener("load", () => resolve(image), { once: true });
    image.addEventListener(
      "error",
      () => reject(new Error("Could not render the plot image.")),
      { once: true },
    );
    image.src = dataUrl;
  });
}

function wrapText(context, text, x, y, maximumWidth, lineHeight) {
  const words = text.split(/\s+/);
  let line = "";
  let currentY = y;
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (line && context.measureText(candidate).width > maximumWidth) {
      context.fillText(line, x, currentY);
      line = word;
      currentY += lineHeight;
    } else {
      line = candidate;
    }
  }
  if (line) {
    context.fillText(line, x, currentY);
  }
}

export function exportCsv(response, appTitle) {
  const columns = [
    { key: "effect_display", label: "effect_display" },
    { key: "effect_working", label: "effect_working" },
    { key: "standardized_distance", label: "standardized_distance" },
    { key: "relative_likelihood", label: "relative_likelihood" },
    { key: "log_relative_likelihood", label: "log_relative_likelihood" },
  ];
  const rows = response.grid.effect_display.map((effectDisplay, index) => ({
    effect_display: effectDisplay,
    effect_working: response.grid.effect_working[index],
    standardized_distance: response.grid.standardized_distance[index],
    relative_likelihood: response.grid.relative_likelihood[index],
    log_relative_likelihood: response.grid.log_relative_likelihood[index],
  }));
  const csv = csvFromRows(columns, rows);
  downloadBlob(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
    `${filenameSlug(appTitle)}.csv`,
  );
}

export async function exportManuscriptPng(plotElement, appTitle) {
  const dataUrl = await globalThis.Plotly.toImage(plotElement, {
    format: "png",
    height: 1000,
    scale: 2,
    width: 1400,
  });
  downloadBlob(
    dataUrlToBlob(dataUrl),
    `${filenameSlug(appTitle)}-manuscript.png`,
  );
}

export async function exportDashboardPng(plotElement, summary, appTitle) {
  const plotDataUrl = await globalThis.Plotly.toImage(plotElement, {
    format: "png",
    height: 900,
    scale: 1,
    width: 1440,
  });
  const plotImage = await loadImage(plotDataUrl);
  const canvas = document.createElement("canvas");
  canvas.width = 1600;
  canvas.height = 1200;
  const context = canvas.getContext("2d");
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#17202a";
  context.font = "700 44px system-ui";
  context.fillText(appTitle, 80, 76, 1440);
  context.font = "25px system-ui";
  wrapText(context, summary, 80, 130, 1440, 34);
  context.drawImage(plotImage, 80, 260, 1440, 900);
  const blob = await canvasBlob(canvas);
  downloadBlob(blob, `${filenameSlug(appTitle)}-dashboard.png`);
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) {
    throw new Error("The browser could not copy the caption.");
  }
}

export async function copyCaption(caption) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(caption);
      return;
    } catch {
      fallbackCopy(caption);
      return;
    }
  }
  fallbackCopy(caption);
}

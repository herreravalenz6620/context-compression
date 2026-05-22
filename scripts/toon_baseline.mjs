#!/usr/bin/env node
// Benchmark-only TOON encoder. Runtime hooks must not depend on this script.

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const INSTRUCTION = "TOON encoded JSON. Interpret this as a lossless TOON representation of the original parsed data.";

async function main() {
  const args = process.argv.slice(2);
  const noInstruction = args.includes("--no-instruction");
  const fallbackRaw = args.includes("--fallback-raw-on-fail");
  const positional = args.filter((arg) => arg !== "--no-instruction" && arg !== "--fallback-raw-on-fail");
  if (positional.length !== 2) {
    usage();
    process.exit(2);
  }

  const [inputPath, outputPath] = positional;
  const toon = await loadToonModule();
  const { output, fellBack } = encodeOrFallback(toon, inputPath, noInstruction, fallbackRaw);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${output}\n`, "utf8");
  if (fellBack) {
    console.error(`TOON round-trip failed for ${inputPath}; wrote raw fallback`);
  }
}

function usage() {
  console.error("Usage: toon_baseline.mjs [--no-instruction] [--fallback-raw-on-fail] <input.json|jsonl|csv|tsv> <output>");
}

async function loadToonModule() {
  try {
    return await import("@toon-format/toon");
  } catch (firstError) {
    for (const candidate of toonModuleCandidates()) {
      try {
        return await import(pathToFileURL(candidate).href);
      } catch {
        // Keep scanning; npm exec exposes packages through PATH rather than NODE_PATH.
      }
    }
    throw new Error(
      "Cannot import @toon-format/toon. Run with a local install or: "
        + "npm exec --yes --package @toon-format/toon@2.3.0 -- "
        + "node scripts/toon_baseline.mjs <input> <output>\n"
        + firstError.message,
    );
  }
}

function* toonModuleCandidates() {
  const pathEntries = (process.env.PATH || "").split(path.delimiter).filter(Boolean);
  for (const entry of pathEntries) {
    if (!entry.endsWith(`${path.sep}node_modules${path.sep}.bin`)) {
      continue;
    }
    yield path.join(path.dirname(entry), "@toon-format", "toon", "dist", "index.mjs");
  }
}

function parseInput(inputPath) {
  const text = fs.readFileSync(inputPath, "utf8").replace(/^\uFEFF/, "");
  const ext = path.extname(inputPath).toLowerCase();
  if (ext === ".json") {
    return JSON.parse(text);
  }
  if (ext === ".jsonl") {
    return text.split(/\r?\n/).filter((line) => line.trim()).map((line) => JSON.parse(line));
  }
  if (ext === ".csv" || ext === ".tsv") {
    return parseDelimited(text, ext === ".tsv" ? "\t" : ",");
  }
  throw new Error(`Unsupported input extension: ${ext}`);
}

function encodeOrFallback(toon, inputPath, noInstruction, fallbackRaw) {
  try {
    const value = parseInput(inputPath);
    const encoded = toon.encode(value);
    const decoded = toon.decode(encoded);
    assertDeepEqual(decoded, value);
    return {
      output: noInstruction ? encoded : `${INSTRUCTION}\n${encoded}`,
      fellBack: false,
    };
  } catch (error) {
    if (!fallbackRaw) {
      throw error;
    }
    const raw = fs.readFileSync(inputPath, "utf8").replace(/^\uFEFF/, "");
    return {
      output: noInstruction
        ? raw
        : `Raw source fallback because TOON did not round-trip this file.\n${raw}`,
      fellBack: true,
    };
  }
}

function parseDelimited(text, delimiter) {
  const rows = parseDelimitedRows(text, delimiter).filter((row) => row.length > 1 || row[0] !== "");
  if (rows.length === 0) {
    return [];
  }
  const [headers, ...dataRows] = rows;
  return dataRows.map((row) => {
    const record = {};
    for (let index = 0; index < headers.length; index += 1) {
      record[headers[index]] = row[index] ?? "";
    }
    return record;
  });
}

function parseDelimitedRows(text, delimiter) {
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (inQuotes) {
      if (char === '"' && next === '"') {
        cell += '"';
        index += 1;
      } else if (char === '"') {
        inQuotes = false;
      } else {
        cell += char;
      }
      continue;
    }
    if (char === '"') {
      inQuotes = true;
    } else if (char === delimiter) {
      row.push(cell);
      cell = "";
    } else if (char === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
    } else if (char !== "\r") {
      cell += char;
    }
  }
  if (cell || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }
  if (inQuotes) {
    throw new Error("Unclosed quoted delimited cell");
  }
  return rows;
}

function assertDeepEqual(actual, expected) {
  const actualJson = JSON.stringify(actual);
  const expectedJson = JSON.stringify(expected);
  if (actualJson !== expectedJson) {
    throw new Error("TOON round-trip changed the parsed source value");
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});

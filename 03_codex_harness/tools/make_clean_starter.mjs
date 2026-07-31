import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";


async function main(sourcePptx, cleanPptx, layoutDir) {
  const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePptx));

  for (const slide of presentation.slides.items) {
    slide.shapes.deleteAll();
    for (const item of [...slide.images.items]) slide.images.deleteById(item.id);
    for (const item of [...slide.tables.items]) slide.tables.deleteById(item.id);
    for (const item of [...slide.charts.items]) slide.charts.deleteById(item.id);
    for (const item of [...slide.artifacts.items]) slide.artifacts.deleteById(item.id);
    // Detach inherited placeholders from the source layout while retaining
    // the imported theme and slide geometry.
    slide.setLayout({ id: "" });
  }

  await fs.mkdir(layoutDir, { recursive: true });
  for (const [index, slide] of presentation.slides.items.entries()) {
    const layout = await slide.export({ format: "layout" });
    const stem = `starter-slide-${String(index + 1).padStart(2, "0")}.layout.json`;
    await fs.writeFile(path.join(layoutDir, stem), await layout.text());
  }

  const output = await PresentationFile.exportPptx(presentation);
  await output.save(cleanPptx);
  console.log(`CLEAN_STARTER=${cleanPptx}`);
  console.log(`LAYOUT_DIR=${layoutDir}`);
}


if (process.argv.length !== 5) {
  console.error("usage: node make_clean_starter.mjs <source.pptx> <clean.pptx> <layout-dir>");
  process.exit(2);
}

main(process.argv[2], process.argv[3], process.argv[4]).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

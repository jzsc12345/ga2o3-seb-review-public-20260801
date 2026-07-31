import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";


const HARNESS = "D:/SILVACO_LOCAL/harness";
const FIG = path.join(HARNESS, "assets", "figures");
const COLORS = {
  navy: "#0F172A",
  ink: "#111827",
  slate: "#475569",
  light: "#F8FAFC",
  border: "#D7DEE7",
  orange: "#F26C32",
  blue: "#2B6CB0",
  green: "#2F855A",
  red: "#C2413B",
  amber: "#D97706",
  purple: "#7C3AED",
  white: "#FFFFFF",
};


async function imageBytes(file) {
  const bytes = await fs.readFile(file);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}


function rect(slide, pos, fill, radius = false, line = COLORS.border) {
  const shape = slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: pos,
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
  });
  shape.bringToFront();
  return shape;
}


function text(slide, value, pos, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: pos,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: style.fontSize ?? 18,
    bold: style.bold ?? false,
    color: style.color ?? COLORS.ink,
    alignment: style.alignment ?? "left",
    verticalAlignment: style.verticalAlignment ?? "top",
    autoFit: style.autoFit ?? "shrinkText",
    wrap: "square",
    insets: style.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    lineSpacing: style.lineSpacing ?? 1.0,
  };
  shape.bringToFront();
  return shape;
}


function page(slide, dark = false) {
  slide.background.fill = dark ? COLORS.navy : COLORS.white;
}


function header(slide, titleValue, subtitleValue, pageNo) {
  text(slide, titleValue, { left: 52, top: 36, width: 1140, height: 48 }, { fontSize: 28, bold: true });
  if (subtitleValue) {
    text(slide, subtitleValue, { left: 52, top: 92, width: 1170, height: 34 }, { fontSize: 13, color: COLORS.slate });
  }
  text(slide, `Ga₂O₃ SEB · evidence audit · ${String(pageNo).padStart(2, "0")}`, { left: 52, top: 686, width: 430, height: 18 }, { fontSize: 9, color: "#94A3B8" });
}


function pill(slide, label, pos, fill) {
  rect(slide, pos, fill, true, fill);
  text(slide, label, pos, { fontSize: 12, bold: true, color: COLORS.white, alignment: "center", verticalAlignment: "middle" });
}


function card(slide, pos, titleValue, body, accent = COLORS.blue) {
  rect(slide, pos, COLORS.light, true, COLORS.border);
  rect(slide, { left: pos.left, top: pos.top, width: 7, height: pos.height }, accent, true, accent);
  text(slide, titleValue, { left: pos.left + 24, top: pos.top + 18, width: pos.width - 40, height: 30 }, { fontSize: 17, bold: true, color: accent });
  text(slide, body, { left: pos.left + 24, top: pos.top + 58, width: pos.width - 40, height: pos.height - 72 }, { fontSize: 12.5, color: COLORS.slate, lineSpacing: 1.08 });
}


async function addImage(slide, fileName, pos, alt, fit = "contain") {
  // Images occupy a lower z-plane than shapes in artifact-tool. Keep the
  // frame transparent so it cannot hide the image it surrounds.
  rect(slide, pos, "none", true, COLORS.border);
  slide.images.add({
    blob: await imageBytes(path.join(FIG, fileName)),
    contentType: "image/png",
    alt,
    fit,
    position: { left: pos.left + 5, top: pos.top + 5, width: pos.width - 10, height: pos.height - 10 },
  });
}


function notes(slide, items) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n${items.map((item) => `- ${item}`).join("\n")}\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}


async function build(starterPptx, output, renderDir) {
  const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPptx));
  if (presentation.slides.items.length !== 14) throw new Error(`expected 14 slides, got ${presentation.slides.items.length}`);

  // Keep the reference deck's theme and geometry, but remove all imported
  // slide content so source text/images cannot leak into this report.
  for (const slide of presentation.slides.items) {
    slide.shapes.deleteAll();
    for (const item of [...slide.images.items]) slide.images.deleteById(item.id);
    for (const item of [...slide.tables.items]) slide.tables.deleteById(item.id);
    for (const item of [...slide.charts.items]) slide.charts.deleteById(item.id);
    for (const item of [...slide.artifacts.items]) slide.artifacts.deleteById(item.id);
  }

  // 1 — title
  {
    const s = presentation.slides.items[0];
    page(s, true);
    text(s, "β-Ga₂O₃ 横向增强型 MOSFET\n单粒子烧毁拟合进展", { left: 74, top: 168, width: 850, height: 150 }, { fontSize: 36, bold: true, color: COLORS.white, lineSpacing: 1.02 });
    text(s, "从“参数调优”转向“持续电流通道的证据审计”", { left: 76, top: 338, width: 760, height: 42 }, { fontSize: 19, color: "#CBD5E1" });
    rect(s, { left: 76, top: 410, width: 170, height: 5 }, COLORS.orange, true, COLORS.orange);
    text(s, "Wang2026 唯一拟合目标 · 截止 2026-08-01", { left: 76, top: 448, width: 640, height: 30 }, { fontSize: 13, color: "#94A3B8" });
    text(s, "证据分界：2026-07-27 09:20 +08:00", { left: 76, top: 486, width: 520, height: 28 }, { fontSize: 12, color: "#94A3B8" });
    text(s, "组会汇报初稿", { left: 1000, top: 618, width: 200, height: 30 }, { fontSize: 14, bold: true, color: COLORS.orange, alignment: "right" });
    notes(s, ["D:/SILVACO_LOCAL/harness/docs/research-results/Ga2O3_SEB_有效进展与拟合审计_20260801.md"]);
  }

  // 2 — dashboard
  {
    const s = presentation.slides.items[1];
    page(s); header(s, "本轮进展一页看板", "输入层已冻结；输出层尚未形成论文中的持续电子导电丝", 2);
    const metrics = [
      ["11,672", "最终网格点", COLORS.green],
      ["0.545%", "收集电荷偏差", COLORS.blue],
      ["394 K", "RUN096 峰值温度", COLORS.amber],
      ["1321 K", "距 Wang 图读差值", COLORS.red],
    ];
    metrics.forEach(([value, label, color], i) => {
      const x = 52 + i * 300;
      rect(s, { left: x, top: 148, width: 275, height: 122 }, COLORS.light, true, COLORS.border);
      text(s, value, { left: x + 20, top: 168, width: 235, height: 46 }, { fontSize: 28, bold: true, color });
      text(s, label, { left: x + 20, top: 222, width: 235, height: 26 }, { fontSize: 12, color: COLORS.slate });
    });
    card(s, { left: 52, top: 304, width: 1176, height: 88 }, "已做实", "几何 / 网格 / 径迹 / 电荷守恒 / 1000 V 长尾基线；RUN095/096 SHA 未漂移。", COLORS.green);
    card(s, { left: 52, top: 410, width: 1176, height: 88 }, "已排除", "完整热源、HfO₂ 热容、Eg(T)、低场 μ(T)、高场 F.VSATN(T) 均不足以解释千 K 级差距。", COLORS.blue);
    card(s, { left: 52, top: 516, width: 1176, height: 104 }, "当前阻塞", "50→100→500 ns 电子路径能力持续下降；1600 V 静态母态未建立；RUN119 在 878.95 V 静态准入失败。", COLORS.red);
    notes(s, ["D:/SILVACO_LOCAL/outputs/runs/RUN096_wang1000-nofp-lgd9-x11-hfo2hc/csv/RUN095_096_hfo2hc_milestones.csv", "D:/SILVACO_LOCAL/outputs/reports/RUN096_109_2d_topology_20260731/csv/RUN096_109_native_vertex_metrics.csv"]);
  }

  // 3 — runner forensic
  {
    const s = presentation.slides.items[2];
    page(s); header(s, "为什么现在没有后台日志窗口？", "求解器没有换：丢的是桌面遗留窗口和只读 monitor", 3);
    await addImage(s, "16_RUN100_tmux_monitor.png", { left: 52, top: 150, width: 540, height: 310 }, "RUN100 read-only tmux monitor");
    await addImage(s, "17_RUN119_bare_desktop.png", { left: 640, top: 150, width: 540, height: 310 }, "RUN119 bare desktop after VM reboot");
    text(s, "RUN100：同一 tmux 发射 + 另开只读 monitor", { left: 52, top: 474, width: 540, height: 30 }, { fontSize: 13, bold: true, color: COLORS.green, alignment: "center" });
    text(s, "RUN119：VM 重启后无 monitor，只剩裸桌面", { left: 640, top: 474, width: 540, height: 30 }, { fontSize: 13, bold: true, color: COLORS.red, alignment: "center" });
    card(s, { left: 52, top: 524, width: 1176, height: 112 }, "取证裁决", "RUN095 / RUN096 / RUN119 正式发射都走 vdoe_tmux.sh start-deck。RUN095/096 截图前台其实是 RUN093 Victory Visual，不是求解日志。今后保持正式 runner 不变，只恢复只读 monitor。", COLORS.orange);
    notes(s, ["D:/SILVACO_LOCAL/outputs/RUN100_boundaryfix_attempt2_live/screenshots/shot_20260730T214614_RUN100_attempt2_tmux.png", "D:/SILVACO_LOCAL/outputs/RUN119_uidnd1e16_short500ns_live/screenshots/shot_20260731T235159_RUN119_1000V_UID2x.png", "D:/SILVACO_LOCAL/scripts/remote/vdoe_tmux.sh"]);
  }

  // 4 — harness architecture
  {
    const s = presentation.slides.items[3];
    page(s); header(s, "07-27 09:20 前后资料已经物理隔离", "Claude skill 不再追加资料；分界后 Markdown 进入独立 harness", 4);
    const items = [
      ["①", "pre-cutoff Git 对象", "540379d · 08:31:21\n冻结包只从 Git object 读取", COLORS.green],
      ["②", "post-cutoff imported", "209 份 Markdown 镜像\n原路径 + SHA + AUTHOR_UNVERIFIED", COLORS.amber],
      ["③", "run evidence", "deck / CSV / PNG / typescript\n原始证据高于后写 handoff", COLORS.blue],
      ["④", "mechanical checks", "结构、清单、SHA、敏感信息\n失败则禁止发布", COLORS.purple],
    ];
    items.forEach(([n, titleValue, body, color], i) => {
      const y = 150 + i * 118;
      rect(s, { left: 72, top: y, width: 1136, height: 94 }, COLORS.light, true, COLORS.border);
      pill(s, n, { left: 90, top: y + 19, width: 60, height: 56 }, color);
      text(s, titleValue, { left: 182, top: y + 18, width: 320, height: 30 }, { fontSize: 18, bold: true, color });
      text(s, body, { left: 520, top: y + 17, width: 650, height: 60 }, { fontSize: 13, color: COLORS.slate });
    });
    text(s, "短 AGENTS 只做目录 → 详细资料按需展开 → 规则由脚本检查 → 周期性垃圾回收", { left: 72, top: 638, width: 1136, height: 28 }, { fontSize: 13, bold: true, color: COLORS.orange, alignment: "center" });
    notes(s, ["https://openai.com/index/harness-engineering/", "D:/SILVACO_LOCAL/harness/ARCHITECTURE.md", "D:/SILVACO_LOCAL/harness/docs/generated/post_cutoff_md_manifest.csv"]);
  }

  // 5 — geometry and charge
  {
    const s = presentation.slides.items[4];
    page(s); header(s, "输入层已经基本对齐：结构、网格、径迹、电荷", "所以主差距不应再归咎于“离子打得不够”", 5);
    await addImage(s, "01_RUN094_mesh.png", { left: 52, top: 146, width: 780, height: 458 }, "RUN094 device geometry and ion-track mesh");
    card(s, { left: 862, top: 146, width: 344, height: 118 }, "最终几何", "20 µm 器件\nLgd = 9 µm · 无场板\nxion = 11 µm", COLORS.green);
    card(s, { left: 862, top: 286, width: 344, height: 118 }, "网格", "11,672 点\n22,992 三角形\n全深度径迹局部细化", COLORS.blue);
    card(s, { left: 862, top: 426, width: 344, height: 148 }, "电荷守恒", "源极收集 2.43622 pC/µm\n目标 2.4230 pC/µm\n偏差 +0.545%", COLORS.orange);
    notes(s, ["D:/SILVACO_LOCAL/outputs/runs/RUN094_wang1000-nofp-lgd9-x11-reference/figs/RUN094_preflight_track_mesh.png", "D:/SILVACO_LOCAL/outputs/runs/RUN094_wang1000-nofp-lgd9-x11-reference/csv/RUN094_final_metrics_and_screen.csv"]);
  }

  // 6 — baseline
  {
    const s = presentation.slides.items[5];
    page(s); header(s, "RUN096：当前冻结的 1000 V 生产基线", "电流完成 100 µs 长尾，但后段仍在衰减，不是持续 SEB", 6);
    await addImage(s, "03_RUN096_baseline.png", { left: 44, top: 142, width: 820, height: 480 }, "RUN095 RUN096 comparison curves and spatial metrics");
    card(s, { left: 892, top: 148, width: 316, height: 130 }, "短时峰值", "Id = 6.711×10⁻⁴ A/µm @31 ps\nTmax = 394.15 K @0.686 ns", COLORS.orange);
    card(s, { left: 892, top: 300, width: 316, height: 130 }, "长尾", "Id(50 ns)=5.63×10⁻⁶\nId(500 ns)=6.57×10⁻⁷\nId(100 µs)=2.19×10⁻⁷ A/µm", COLORS.blue);
    card(s, { left: 892, top: 452, width: 316, height: 130 }, "物理判读", "离子打开的路正在重新关门\n→ 更像可恢复 SET\n→ 尚无持续 J·E 发热", COLORS.red);
    notes(s, ["D:/SILVACO_LOCAL/outputs/runs/RUN096_wang1000-nofp-lgd9-x11-hfo2hc/figs/RUN095_096_hfo2hc_comparison.png", "D:/SILVACO_LOCAL/outputs/runs/RUN096_wang1000-nofp-lgd9-x11-hfo2hc/csv/RUN095_096_hfo2hc_milestones.csv"]);
  }

  // 7 — OFAT
  {
    const s = presentation.slides.items[6];
    page(s); header(s, "系统 OFAT 已经排除五个“看起来最像答案”的旋钮", "千 K 温差不是靠多开一个热源或温变系数就能补出来", 7);
    await addImage(s, "13_fit_gap_dashboard.png", { left: 46, top: 140, width: 1188, height: 500 }, "Temperature gap and OFAT effect sizes");
    notes(s, ["D:/SILVACO_LOCAL/harness/assets/figures/13_fit_gap_dashboard.png", "D:/SILVACO_LOCAL/outputs/runs/RUN103_wang1000-nofp-lgd9-x11-mobt-ma18/csv/RUN096_102_103_tempfeedback_peaks.csv", "D:/SILVACO_LOCAL/outputs/runs/RUN118_wang1000-fvsatt-short500ns/csv/RUN096_118_fvsatn_peaks.csv"]);
  }

  // 8 — topology
  {
    const s = presentation.slides.items[7];
    page(s); header(s, "真正接近根因的证据：持续电流路径在几十到几百 ns 断掉", "没有电流，温度反馈再强也没有足够 J·E 功率", 8);
    await addImage(s, "06_current_path_topology.png", { left: 46, top: 140, width: 850, height: 492 }, "RUN096 RUN109 native vertex current paths");
    card(s, { left: 928, top: 150, width: 300, height: 128 }, "50 ns", "路径能力约 189.7 A/cm²\n导电丝仍连续", COLORS.green);
    card(s, { left: 928, top: 300, width: 300, height: 128 }, "100 ns", "下降到约 62.8 A/cm²\n瓶颈开始收缩", COLORS.amber);
    card(s, { left: 928, top: 450, width: 300, height: 128 }, "500 ns", "只剩约 13.6 A/cm²\n持续电流丝未建立", COLORS.red);
    notes(s, ["D:/SILVACO_LOCAL/outputs/reports/RUN096_109_2d_topology_20260731/figs/RUN096_109_native_vertex_paths.png", "D:/SILVACO_LOCAL/outputs/reports/RUN096_109_2d_topology_20260731/csv/RUN096_109_native_vertex_metrics.csv"]);
  }

  // 9 — substrate/UID
  {
    const s = presentation.slides.items[8];
    page(s); header(s, "衬底/UID 调整只改变“电流走哪条路”，没有增加后段端电流", "局部改善 ≠ 漏—源通路真正接通", 9);
    await addImage(s, "07_ndsub_terminal_overlay.png", { left: 48, top: 142, width: 820, height: 490 }, "RUN096 RUN108 RUN109 terminal current overlay");
    card(s, { left: 900, top: 156, width: 312, height: 152 }, "观察", "局部路径能力可提高约 17%–23%\n但 100/500 ns 端电流不增", COLORS.blue);
    card(s, { left: 900, top: 334, width: 312, height: 152 }, "解释", "电流只是重新分配\n（绕路更顺，但总水量没增加）", COLORS.orange);
    card(s, { left: 900, top: 512, width: 312, height: 92 }, "裁决", "关闭盲扫 UID donor 主因路线", COLORS.red);
    notes(s, ["D:/SILVACO_LOCAL/outputs/reports/RUN096_108_109_ndsub_path_overlay_20260731/figs/RUN096_108_109_terminal_curves_overlay.png"]);
  }

  // 10 — static walls
  {
    const s = presentation.slides.items[9];
    page(s); header(s, "两个静态准入墙：没有合格母态，就没有资格讨论 1600 V / 500 ns", "失败是数值准入失败，不是过流或物理 SEB", 10);
    await addImage(s, "09_static1600_gate.png", { left: 48, top: 150, width: 560, height: 360 }, "RUN104 RUN107 static reach");
    await addImage(s, "10_RUN119_static_fail.png", { left: 672, top: 150, width: 560, height: 360 }, "RUN119 static gate failure");
    text(s, "RUN104–107：目标 1600 V，只到 1033.8–1098.5 V", { left: 48, top: 530, width: 560, height: 44 }, { fontSize: 13, bold: true, color: COLORS.red, alignment: "center" });
    text(s, "RUN119：878.9508 V 后 16 次折半，首个 2 ps 前停止", { left: 672, top: 530, width: 560, height: 44 }, { fontSize: 13, bold: true, color: COLORS.red, alignment: "center" });
    text(s, "合规结论：NO VALID TRANSIENT；不得写成“UID 已在 500 ns 被证伪”", { left: 120, top: 602, width: 1040, height: 32 }, { fontSize: 15, bold: true, color: COLORS.orange, alignment: "center" });
    notes(s, ["D:/SILVACO_LOCAL/outputs/reports/RUN104_107_vds_ndsub_adjudication_20260731/figs/RUN104_107_ndsub_static_reach.png", "D:/SILVACO_LOCAL/outputs/runs/RUN119_wang1000-uidnd1e16-short500ns/figs/RUN119_static_gate_fail_878p950806V.png"]);
  }

  // 11 — historical achievements
  {
    const s = presentation.slides.items[10];
    page(s); header(s, "两个“看起来成功、但不能冒充最终拟合”的历史结果", "它们仍有价值：一个校准阈值，一个验证高压数值链", 11);
    await addImage(s, "12_RUN053_idvg.png", { left: 50, top: 150, width: 550, height: 350 }, "RUN053 threshold calibration");
    await addImage(s, "11_RUN082_static_bv.png", { left: 680, top: 150, width: 550, height: 350 }, "RUN082 static electrothermal voltage sweep");
    card(s, { left: 50, top: 526, width: 550, height: 110 }, "RUN053 · 可用产出", "Vth = 0.9089 V，接近 0.9 V；但不是最终无场板 / Lgd9 几何。", COLORS.green);
    card(s, { left: 680, top: 526, width: 550, height: 110 }, "RUN082 · 不可越权", "到 2707.2 V，但 Id≈2.92×10⁻¹⁵ A/µm、T≈300 K；不是 Wang Fig.2 击穿支路。", COLORS.red);
    notes(s, ["D:/SILVACO_LOCAL/outputs/runs/RUN053_lgd14-subfe-wf578-idvg/figs/RUN052_053_IdVg_wf_calibration.png", "D:/SILVACO_LOCAL/outputs/runs/RUN082_wang-static-et/figs/RUN082_staticET_Id_T_vs_V.png"]);
  }

  // 12 — context matrix
  {
    const s = presentation.slides.items[11];
    page(s); header(s, "Wang2026 的四个图级目标必须分开验收", "当前没有一项达到同条件、同支路、同判据的闭环", 12);
    await addImage(s, "15_wang_context_matrix.png", { left: 44, top: 138, width: 1192, height: 510 }, "Wang 2026 four-context acceptance matrix");
    notes(s, ["D:/SILVACO_LOCAL/harness/assets/figures/15_wang_context_matrix.png", "D:/SILVACO_LOCAL/archive/Wang 等 - 2026 - ###nihe_Simulation of the single event burnout in lateral enhancement mode β-Ga2 O3.pdf"]);
  }

  // 13 — 8 week plan
  {
    const s = presentation.slides.items[12];
    page(s); header(s, "未来八周：先补空间证据，再决定下一枪", "目标是两个月内形成一篇诚实、可复现、有方法创新的小论文", 13);
    const weeks = [
      ["W1–2", "恢复可见反馈", "只读 tmux monitor\nRUN096 四时刻 Je/Joule/electron/trap 同色标图\n定位真正断点", COLORS.green],
      ["W3–4", "持续通道单变量", "新 A13/A14 核签\n只改势垒/面电荷一个变量\n拒绝 solver 盲调", COLORS.blue],
      ["W5–6", "论文目标配对", "最终几何 1200 V Fig.4\n若静态母态通过，再做 1600 V Fig.6/7", COLORS.orange],
      ["W7–8", "加固与收口", "基线通过后才比较 SC-HEP\n补表格、不确定度、图注和复现包", COLORS.purple],
    ];
    weeks.forEach(([week, titleValue, body, color], i) => {
      const x = 52 + i * 300;
      rect(s, { left: x, top: 154, width: 275, height: 352 }, COLORS.light, true, COLORS.border);
      pill(s, week, { left: x + 18, top: 174, width: 82, height: 38 }, color);
      text(s, titleValue, { left: x + 18, top: 236, width: 235, height: 40 }, { fontSize: 18, bold: true, color });
      text(s, body, { left: x + 18, top: 296, width: 235, height: 170 }, { fontSize: 13, color: COLORS.slate, lineSpacing: 1.12 });
    });
    card(s, { left: 52, top: 540, width: 1176, height: 104 }, "推荐裁决", "下一枪不是继续调 VSAT 或 UID 掺杂，而是先用 RUN096 现成 STR 补齐四时刻空间连通图；断点找准后，再做一个可证伪的势垒/面电荷 OFAT。", COLORS.orange);
    notes(s, ["D:/SILVACO_LOCAL/harness/docs/research-results/小论文图表补充清单_20260801.md", "D:/SILVACO_LOCAL/harness/docs/exec-plans/active/20260801_cutoff_freeze_and_report.md"]);
  }

  // 14 — conclusion
  {
    const s = presentation.slides.items[13];
    page(s, true);
    text(s, "结论", { left: 70, top: 64, width: 240, height: 48 }, { fontSize: 31, bold: true, color: COLORS.white });
    const conclusions = [
      ["①", "RUN095/096 没有因为重连而丢失；日志窗差异来自 GUI 遗留与 monitor 缺失。"],
      ["②", "几何、网格、径迹和电荷已基本对齐；RUN096 是当前冻结的 1000 V 基线。"],
      ["③", "五个温度/迁移率旋钮的实测效应太小，主缺项是几十到几百 ns 的持续电子通道。"],
      ["④", "当前尚未复现 Wang Fig.2/3/4/6–7；RUN119 只有静态准入失败，没有有效瞬态。"],
      ["⑤", "分界后 209 份 Markdown 已进入 harness 隔离层，不再污染 Claude skill。"],
    ];
    conclusions.forEach(([n, body], i) => {
      const y = 150 + i * 88;
      text(s, n, { left: 82, top: y, width: 48, height: 42 }, { fontSize: 20, bold: true, color: COLORS.orange, alignment: "center" });
      text(s, body, { left: 150, top: y, width: 1030, height: 54 }, { fontSize: 17, color: "#E2E8F0" });
    });
    rect(s, { left: 82, top: 610, width: 1098, height: 1 }, "#334155", false, "#334155");
    text(s, "下一步：空间断点 → 单变量势垒/面电荷 → 1200 V 配对 → 1600 V 空间复现", { left: 82, top: 638, width: 1098, height: 34 }, { fontSize: 15, bold: true, color: COLORS.orange, alignment: "center" });
    notes(s, ["D:/SILVACO_LOCAL/harness/docs/research-results/Ga2O3_SEB_有效进展与拟合审计_20260801.md"]);
  }

  await fs.mkdir(renderDir, { recursive: true });
  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(path.join(renderDir, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(renderDir, `${stem}.layout.json`), await layout.text());
  }
  const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(path.join(renderDir, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));
  const inspect = await presentation.inspect({ kind: "slide,textbox,image,notes", maxChars: 50000 });
  await fs.writeFile(path.join(renderDir, "final-inspect.ndjson"), inspect.ndjson, "utf8");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(output);
  console.log(`OUTPUT=${output}`);
  console.log(`RENDER_DIR=${renderDir}`);
}


if (process.argv.length !== 5) {
  console.error("usage: node build_advisor_ppt.mjs <starter.pptx> <output.pptx> <render-dir>");
  process.exit(2);
}

build(process.argv[2], process.argv[3], process.argv[4]).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

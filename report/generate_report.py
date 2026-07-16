#!/usr/bin/env python3
"""Generate the Mini Assignment #2 PDF from committed result artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "report" / "data"
NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#2F6B9A")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#E9C46A")
RED = colors.HexColor("#C94C4C")
LIGHT = colors.HexColor("#F3F6F8")
MID = colors.HexColor("#D7E0E7")
TEXT = colors.HexColor("#24313A")
MUTED = colors.HexColor("#5D6B75")


def load_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 15 * mm, width, 15 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 9.5 * mm, "Mini Assignment #2 - BrainHIVE Retrieval")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=8 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=BLUE,
            spaceAfter=8 * mm,
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=NAVY,
            spaceBefore=2 * mm,
            spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=BLUE,
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13.2,
            textColor=TEXT,
            spaceAfter=2.3 * mm,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10,
            textColor=TEXT,
        ),
        "note": ParagraphStyle(
            "NoteCustom",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=14.5,
            textColor=NAVY,
            backColor=colors.HexColor("#E8F3F1"),
            borderColor=TEAL,
            borderWidth=0.8,
            borderPadding=8,
            spaceBefore=2 * mm,
            spaceAfter=4 * mm,
        ),
        "warning": ParagraphStyle(
            "WarningCustom",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.4,
            leading=13.2,
            textColor=colors.HexColor("#6D2525"),
            backColor=colors.HexColor("#FBECEC"),
            borderColor=RED,
            borderWidth=0.8,
            borderPadding=8,
            spaceAfter=4 * mm,
        ),
        "center": ParagraphStyle(
            "CenterSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=TEXT,
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def styled_table(rows, widths, header=True, font_size=8, row_backgrounds=None) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.35, MID),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    if row_backgrounds:
        for row_index, color in row_backgrounds.items():
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), color))
    table.setStyle(TableStyle(commands))
    return table


def result_chart() -> Drawing:
    values = [51.2, 48.8, 73.7, 69.7, 83.0, 81.0, 94.1, 92.95]
    labels = ["Paper", "Repro", "Paper", "Repro", "Paper", "Repro", "Paper", "Repro"]
    colors_list = [BLUE, TEAL, BLUE, TEAL, BLUE, TEAL, BLUE, TEAL]
    drawing = Drawing(465, 180)
    drawing.add(String(4, 164, "Ten-subject retrieval accuracy (%)", fontName="Helvetica-Bold", fontSize=10, fillColor=NAVY))
    base_y = 25
    max_h = 120
    bar_w = 38
    gap = 18
    starts = [20, 125, 230, 335]
    group_names = ["B32 Top-1", "B32+VAE Top-1", "B32 Top-5", "B32+VAE Top-5"]
    for tick in range(0, 101, 20):
        y = base_y + max_h * tick / 100
        drawing.add(Rect(15, y, 425, 0.3, fillColor=MID, strokeColor=None))
        drawing.add(String(0, y - 2, str(tick), fontSize=6.5, fillColor=MUTED))
    for group, start in enumerate(starts):
        for offset in range(2):
            index = group * 2 + offset
            height = max_h * values[index] / 100
            x = start + offset * (bar_w + 4)
            drawing.add(Rect(x, base_y, bar_w, height, fillColor=colors_list[index], strokeColor=None))
            drawing.add(String(x + bar_w / 2, base_y + height + 3, f"{values[index]:.1f}", textAnchor="middle", fontSize=7, fillColor=TEXT))
            drawing.add(String(x + bar_w / 2, 13, labels[index], textAnchor="middle", fontSize=6.5, fillColor=MUTED))
        drawing.add(String(start + bar_w + 2, 2, group_names[group], textAnchor="middle", fontSize=7.2, fillColor=NAVY))
    return drawing


def build_story(s: dict[str, ParagraphStyle]):
    b32 = load_csv("canonical_b32_summary.csv")
    fusion = load_csv("canonical_b32_vae_summary.csv")
    b32_subjects = [row for row in b32 if row["subject"] != "MEAN"]
    fusion_subjects = [row for row in fusion if row["subject"] != "MEAN"]
    story = []

    story.extend(
        [
            Spacer(1, 17 * mm),
            p("BrainHIVE Retrieval Reproduction", s["title"]),
            p("Corrected reproduction of the B32 versus B32+VAE ablation on THINGS-EEG", s["subtitle"]),
            HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=8 * mm),
            styled_table(
                [
                    ["Student", "Yuhui Zheng"],
                    ["Paper", "Learning Brain Representation with Hierarchical Visual Embeddings (ICLR 2026)"],
                    ["Target", "Intra-subject 200-way zero-shot retrieval, B32 versus B32+VAE"],
                    ["Repository", "github.com/HUI-HUI-lab/brainhive-retrieval-reproduction"],
                    ["Corrected run", "16 July 2026 - 10 subjects, 20 formal runs"],
                ],
                [35 * mm, 125 * mm],
                header=False,
                font_size=9,
                row_backgrounds={0: LIGHT, 2: LIGHT, 4: LIGHT},
            ),
            Spacer(1, 8 * mm),
            p(
                "Outcome: canonical B32 features raised the reproduced mean to <b>48.8%/81.0%</b> Top-1/Top-5. "
                "B32+VAE reached <b>69.7%/92.95%</b>. The reproduced VAE gain (+20.9/+11.95 points) closely matches "
                "the paper's detailed Table 7 gain (+22.5/+11.1 points).",
                s["note"],
            ),
            p(
                "Scope: this is one representative ablation. Reconstruction, diffusion-prior training, inter-subject retrieval, "
                "and other visual encoders are outside scope.",
                s["body"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("1. Paper and reproduction target", s["h1"]),
            p(
                "BrainHIVE aligns brain signals with a fused hierarchy of visual representations. The selected experiment asks "
                "whether adding low-level SDXL VAE information to semantic LAION CLIP ViT-B/32 features improves 200-way "
                "THINGS-EEG retrieval. The paper reports aggregate values in Table 3 and detailed per-subject values in Table 7. "
                "Table 7 is used for the primary corrected comparison because it exposes the same ten paired subjects.",
                s["body"],
            ),
            p("2. Original and reproduced settings", s["h1"]),
            styled_table(
                [
                    ["Component", "Paper", "Corrected reproduction"],
                    ["Task", "THINGS-EEG intra-subject, 200-way", "Same; all ten subjects"],
                    ["EEG", "17 O+P channels; trials averaged", "Same; validated 17x250 tensors"],
                    ["Targets", "LAION B32; B32+SDXL VAE", "Canonical B32 512-D; verified VAE 1024-D"],
                    ["Training", "25 epochs; AdamW; LR 5e-4; batch 1024", "Same; one seed (2025); 10-step warmup"],
                    ["Metric", "Top-1/Top-5 over 200 candidates", "Same; evaluation batch 200"],
                    ["Compute", "Single RTX 5090 reported for contrastive stage", "CPU FP32; four concurrent workers"],
                    ["Runs", "Averages; public launcher repeats 3x", "One run/subject/setting"],
                ],
                [30 * mm, 60 * mm, 75 * mm],
                font_size=7.7,
                row_backgrounds={2: LIGHT, 4: LIGHT, 6: LIGHT},
            ),
            Spacer(1, 4 * mm),
            p(
                "Each subject contained 16,540 averaged training examples and 200 averaged test examples. Preflight checks "
                "verified sample counts, dimensions, finite values, unique image IDs, and EEG-to-embedding alignment before training.",
                s["body"],
            ),
            p("Controlled modifications", s["h2"]),
            p(
                "The original LLM is irrelevant to this retrieval stage. One seed replaced repeated runs. CPU FP32 was used because "
                "both shared GPUs were occupied; optimizer, batch size, epochs, channels, warmup, loss, and evaluation remained fixed.",
                s["body"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("3. Cache audit and failed first attempt", s["h1"]),
            p(
                "The first ten-subject run used the public Hugging Face files named as B32 and produced 21.6%/53.05%. "
                "B32+VAE produced 50.2%/82.55%. Rather than attributing the entire gap to random seed or precision, the visual targets "
                "were inspected directly.",
                s["body"],
            ),
            p(
                "The public B32 cache was severely collapsed: unrelated image vectors were almost parallel. It should not be used "
                "for this experiment without validation.",
                s["warning"],
            ),
            styled_table(
                [
                    ["Diagnostic", "Canonical / trusted B32", "Public HF B32"],
                    ["Random-pair cosine median", "0.3264", "0.9943"],
                    ["Random-pair cosine mean", "0.3300", "0.9915"],
                    ["Normalized mean-vector norm", "0.5745", "0.9957"],
                    ["Same image vs fresh official extraction", "0.99992", "0.20091"],
                    ["Nearest-neighbor row recovery (sample 256)", "Expected semantic structure", "0/256 correct rows"],
                ],
                [67 * mm, 48 * mm, 48 * mm],
                font_size=8,
                row_backgrounds={2: LIGHT, 4: LIGHT},
            ),
            Spacer(1, 4 * mm),
            p(
                "Image IDs, ordering, dimensions, and row counts were correct, so a simple shard-order bug was ruled out. A fresh "
                "embedding for the same source image matched the trusted cache almost exactly but not the public cache. The exact "
                "upstream generation or upload error cannot be recovered from the available metadata.",
                s["body"],
            ),
            p("Corrective action", s["h2"]),
            p(
                "The corrected run used a trusted read-only B32 cache verified against the canonical model and canonical preprocessing. "
                "The VAE cache was retained because its random-pair cosine median (0.0426) and alignment checks were healthy. The "
                "repository now includes a mandatory collapse detector and excludes public B32 from default downloads.",
                s["body"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("4. Corrected results", s["h1"]),
            styled_table(
                [
                    ["Source / setting", "Top-1 (%)", "Top-5 (%)", "VAE gain (pp)"],
                    ["Paper Table 7 - B32", "51.2", "83.0", "-"],
                    ["Paper Table 7 - B32+VAE", "73.7", "94.1", "+22.5 / +11.1"],
                    ["Corrected reproduction - B32", "48.8", "81.0", "-"],
                    ["Corrected reproduction - B32+VAE", "69.7", "92.95", "+20.9 / +11.95"],
                ],
                [75 * mm, 28 * mm, 28 * mm, 34 * mm],
                font_size=8.3,
                row_backgrounds={2: LIGHT, 4: colors.HexColor("#E8F3F1")},
            ),
            Spacer(1, 3 * mm),
            result_chart(),
            p(
                "The corrected absolute gap is small: -2.4/-2.0 points for B32 and -4.0/-1.15 points for B32+VAE relative to "
                "Table 7. Exact agreement is not required by the assignment, and the paired improvement is the main target.",
                s["note"],
            ),
            PageBreak(),
        ]
    )

    subject_rows = [["Subj", "B32 T1", "B32 T5", "B32+VAE T1", "B32+VAE T5", "T1 gain", "T5 gain"]]
    for left, right in zip(b32_subjects, fusion_subjects):
        b1 = float(left["eval_top1_acc"]) * 100
        b5 = float(left["eval_top5_acc"]) * 100
        f1 = float(right["eval_top1_acc"]) * 100
        f5 = float(right["eval_top5_acc"]) * 100
        subject_rows.append(
            [left["subject"], f"{b1:.1f}", f"{b5:.1f}", f"{f1:.1f}", f"{f5:.1f}", f"+{f1-b1:.1f}", f"+{f5-b5:.1f}"]
        )
    subject_rows.append(["Mean", "48.8", "81.0", "69.7", "93.0", "+20.9", "+12.0"])
    story.extend(
        [
            p("5. Per-subject result and interpretation", s["h1"]),
            styled_table(
                subject_rows,
                [15 * mm, 21 * mm, 21 * mm, 29 * mm, 29 * mm, 22 * mm, 22 * mm],
                font_size=7.8,
                row_backgrounds={2: LIGHT, 4: LIGHT, 6: LIGHT, 8: LIGHT, 10: LIGHT, 11: colors.HexColor("#E8F3F1")},
            ),
            Spacer(1, 4 * mm),
            p("Is the paper's conclusion supported?", s["h2"]),
            p(
                "Yes. B32+VAE improves both Top-1 and Top-5 for every reproduced subject. The mean Top-1 gain differs from the "
                "paper by only 1.6 points, and the mean Top-5 gain differs by 0.85 points. This is a clear reproduction of the "
                "reported performance trend and approximately supports the paper's conclusion that low-level VAE features "
                "complement high-level CLIP semantics.",
                s["body"],
            ),
            p("Remaining differences", s["h2"]),
            p(
                "The remaining 1-4 point absolute gaps are consistent with one seed instead of repeated runs, CPU FP32 numerical "
                "behavior, dependency and code-snapshot drift, and small internal differences between the paper's aggregate tables. "
                "The corrected result is much closer to the paper than to the failed public-cache run, confirming that target-feature "
                "quality was the dominant discrepancy.",
                s["body"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("6. AI-assisted workflow", s["h1"]),
            p(
                "Codex assisted with repository inspection, experiment design, code changes, SSH diagnostics, cache forensics, "
                "data validation, job monitoring, aggregation, documentation, and PDF generation. Human decisions selected the "
                "target, approved server access, authorized execution, and accepted the CPU fallback when shared GPUs were busy.",
                s["body"],
            ),
            styled_table(
                [
                    ["Purpose", "Representative prompt / action"],
                    ["Planning", "Inspect BrainHIVE and design a minimal Table 3 retrieval reproduction."],
                    ["Execution", "Check resources, validate data, run one subject, then run all ten subjects safely."],
                    ["Diagnosis", "Why is the reproduction far below the paper? Compare embeddings before changing training."],
                    ["Cache audit", "Recompute one canonical B32 feature and test whether the public cache is permuted or collapsed."],
                    ["Correction", "Use verified B32, rerun B32 and B32+VAE for all subjects, aggregate, and update deliverables."],
                ],
                [35 * mm, 130 * mm],
                font_size=8,
                row_backgrounds={2: LIGHT, 4: LIGHT},
            ),
            p("7. Runtime, cost, and reproducibility", s["h1"]),
            styled_table(
                [
                    ["Resource", "Recorded / estimated value"],
                    ["Corrected formal runs", "20/20 successful; 25 epochs each"],
                    ["Matrix wall time", "Approximately 17 min 47 s with four CPU workers"],
                    ["Summed runtime", "3,867 s; mean 193.35 s/run"],
                    ["AI-assisted time", "Approximately 4 hours across planning, debugging, execution, and writing"],
                    ["AI token usage", "Approximately 200k tokens; account export unavailable"],
                    ["Incremental AI cost", "Not separately metered; Codex account/subscription usage"],
                ],
                [48 * mm, 117 * mm],
                font_size=8,
                row_backgrounds={2: LIGHT, 4: LIGHT, 6: LIGHT},
            ),
            p("Commands", s["h2"]),
            p(
                "<font name='Courier'>python reproduction/scripts/validate_embeddings.py --data-root DATA</font><br/>"
                "<font name='Courier'>python reproduction/scripts/validate_data.py --data-root DATA --subjects 1 --models CLIP-ViT-B-32-laion2B-s34B-b79K vae</font><br/>"
                "<font name='Courier'>PRECISION=fp32 USE_CPU=true MAX_PARALLEL=4 bash reproduction/scripts/run_matrix.sh DATA RESULTS 1,2,3,4,5,6,7,8,9,10 2025</font>",
                s["small"],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("8. Limitations and deliverables", s["h1"]),
            p(
                "Only one seed was run. The exact internal paper snapshot and original cached features were unavailable. The corrected "
                "run reused a trusted canonical cache after direct official-model verification rather than regenerating all 16,740 "
                "images. CPU FP32 differs from the paper's GPU execution. Approximate AI token, time, and cost values should be replaced "
                "with account-exported figures if available.",
                s["body"],
            ),
            p(
                "The repository contains runnable code, pinned dependencies, safe data-preparation instructions, cache and alignment "
                "validators, CPU/GPU launch commands, aggregation scripts, machine-readable results, this PDF, HowTo.md, and a reusable "
                "research-server skill. Large datasets, caches, checkpoints, credentials, private keys, and private infrastructure "
                "details are not committed.",
                s["note"],
            ),
            p("Repository", s["h2"]),
            p(
                "<link href='https://github.com/HUI-HUI-lab/brainhive-retrieval-reproduction' color='#2F6B9A'>"
                "https://github.com/HUI-HUI-lab/brainhive-retrieval-reproduction</link>",
                s["body"],
            ),
            p("References", s["h2"]),
            p(
                "[1] Zheng, J. et al. <i>Learning Brain Representation with Hierarchical Visual Embeddings</i>. ICLR 2026. "
                "<link href='https://arxiv.org/abs/2602.07495' color='#2F6B9A'>arXiv:2602.07495</link><br/>"
                "[2] BrainHIVE source. <link href='https://github.com/ssshamiii/Brain-HIVE' color='#2F6B9A'>github.com/ssshamiii/Brain-HIVE</link><br/>"
                "[3] THINGS-EEG. <link href='https://huggingface.co/datasets/Haitao999/things-eeg' color='#2F6B9A'>Hugging Face dataset</link><br/>"
                "[4] Public visual cache inspected in the failed first attempt. "
                "<link href='https://huggingface.co/datasets/fakekungfu/Brain-HIVE_Visual_Embeddings' color='#2F6B9A'>Hugging Face dataset</link>",
                s["body"],
            ),
        ]
    )
    return story


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "report.pdf")
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=17 * mm,
        title="BrainHIVE Retrieval Reproduction",
        author="Yuhui Zheng",
        subject="Mini Assignment #2",
    )
    document.build(build_story(styles()), onFirstPage=page_decor, onLaterPages=page_decor)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

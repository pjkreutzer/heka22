#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "text2qti",
# ]
# ///

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

POINT_MAP = {
    "Recall": 1,
    "Contrast": 1,
    "Apply": 2,
    "Analyze": 2,
    "Evaluate": 2,
    "Synth": 2,
    "Synthesize": 2,
}

# How many questions to pick from each point‑value pool
PICK_MAP = {
    1: 6,  # 6 one‑point questions per student
    2: 2,  # 2 two‑point questions per student
}

# ============================================================
# UPDATED REGEX – stops before next question header, not ---
# ============================================================

QUESTION_RE = re.compile(
    r"""
    \*\*Q(?P<qid>\d+)
    \s+\[
        (?P<lecture>L\d)
        \s*/\s*
        (?P<lo>LO\d)
        \s*/\s*
        (?P<cognitive>[^\]]+)
    \]\*\*
    \s*
    (?P<question>.*?)
    \n
    (?P<choices>(?:- .*?\n)+)
    \n?
    \*Feedback:\*
    \s*(?P<feedback>.*?)
    (?=\n\*\*Q| \Z)           # <--- stop at next **Q or end of file
    """,
    re.DOTALL | re.VERBOSE,
)

CHOICE_RE = re.compile(
    r"^- (?P<correct>\*\*\[\*\]\*\*|\[\*\])?\s*(?P<label>[A-Z]\))?\s*(?P<text>.+)$"
)


# ============================================================
# HELPERS
# ============================================================


def points_for(cognitive: str) -> int:
    try:
        return POINT_MAP[cognitive]
    except KeyError:
        raise ValueError(f"Unknown cognitive level: {cognitive}")


def indent_text_block(text: str, indent_spaces: int = 4) -> str:
    """Indent continuation lines so text2qti sees them as part of the same block."""
    lines = text.splitlines()
    if len(lines) <= 1:
        return text
    first = lines[0]
    prefix = " " * indent_spaces
    new_lines = [first]
    for line in lines[1:]:
        if line.strip() == "":
            new_lines.append("")  # blank line = paragraph break
        else:
            new_lines.append(prefix + line)
    return "\n".join(new_lines)


# ============================================================
# PARSE SOURCE MARKDOWN
# ============================================================


def parse_questions(markdown: str) -> list[dict]:

    questions = []

    for match in QUESTION_RE.finditer(markdown):
        qid = match.group("qid")
        lecture = match.group("lecture")
        lo = match.group("lo")
        cognitive = match.group("cognitive").strip()
        question = match.group("question").strip()
        feedback = match.group("feedback").strip()

        points = points_for(cognitive)

        choices = []
        correct = None

        for line in match.group("choices").strip().splitlines():
            choice_match = CHOICE_RE.match(line.strip())
            if not choice_match:
                continue

            text = choice_match.group("text").strip()
            is_correct = choice_match.group("correct") is not None

            choices.append({"text": text, "correct": is_correct})
            if is_correct:
                correct = text

        if correct is None:
            raise ValueError(f"No correct answer for Q{qid}")

        questions.append(
            {
                "qid": qid,
                "lecture": lecture,
                "lo": lo,
                "cognitive": cognitive,
                "points": points,
                "question": question,
                "choices": choices,
                "feedback": feedback,
            }
        )

    return questions


# ============================================================
# BUILD TEXT2QTI SOURCE (pool by points, fixed picks)
# ============================================================


def render_question(q: dict) -> str:
    out = []
    out.append(f"Title: Q{q['qid']} - {q['cognitive']} ({q['lo']})")
    out.append(f"Points: {q['points']}")

    question_text = indent_text_block(q["question"], indent_spaces=4)
    out.append(f"1.  {question_text}")

    if q["feedback"]:
        feedback_text = indent_text_block(q["feedback"], indent_spaces=4)
        out.append(f"... {feedback_text}")

    labels = "abcdefghijklmnopqrstuvwxyz"
    for i, choice in enumerate(q["choices"]):
        if choice["correct"]:
            out.append(f"*{labels[i]}) {choice['text']}")
        else:
            out.append(f"{labels[i]}) {choice['text']}")

    out.append("")
    return "\n".join(out)


def build_text2qti(questions: list[dict]) -> str:
    out = []
    out.append("Quiz title: Foundations of Ecological Economics")
    out.append(
        "Quiz description: This multiple choice quiz tests your understanding of the first four lectures, the foundations of ecological economics. You may use all literature and course resources presented so far; you may not use AI. This quiz will give you up to 20 bonus points towards the final exam grade."
    )
    out.append("")
    out.append("shuffle answers: true")
    out.append("show correct answers: true")
    out.append("one question at a time: false")
    out.append("")
    # Group questions by point value only
    grouped = defaultdict(list)
    for q in questions:
        grouped[q["points"]].append(q)

    # First the 1‑point pool, then the 2‑point pool
    for points in sorted(grouped.keys()):
        group_questions = grouped[points]
        pick = PICK_MAP.get(points, len(group_questions))  # fallback: all questions

        # Ensure we don't ask for more than available
        actual_pick = min(pick, len(group_questions))

        out.append("GROUP")
        out.append(f"pick: {actual_pick}")
        out.append(f"points per question: {points}")
        out.append("")

        for q in group_questions:
            out.append(render_question(q))

        out.append("END_GROUP")
        out.append("")

    return "\n".join(out)


# ============================================================
# MAIN
# ============================================================


def main():
    if len(sys.argv) != 2:
        print("Usage:  ./build_qti.py quiz.md")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    markdown = source_path.read_text(encoding="utf-8")
    questions = parse_questions(markdown)
    print(f"Parsed {len(questions)} questions")

    generated = build_text2qti(questions)

    intermediate = source_path.with_suffix(".text2qti.txt")
    intermediate.write_text(generated, encoding="utf-8")
    print(f"Wrote intermediate file: {intermediate}")

    cmd = ["text2qti", str(intermediate)]
    print("\nRunning text2qti...")
    subprocess.run(cmd, check=True)

    output_zip = intermediate.with_suffix(".zip")
    if output_zip.exists():
        print("\n✓ Created QTI package:")
        print(f"  {output_zip}")
    else:
        print("\n✗ QTI package was not created. Check for errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

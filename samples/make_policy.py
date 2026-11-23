"""Generate samples/motor_policy.pdf: a 3-page fictional motor insurance policy.

All names, numbers and terms are invented sample data for testing document Q&A.
Run: python samples/make_policy.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "motor_policy.pdf"

COMPANY = "Covexa General Insurance Ltd."
POLICY_NO = "CVX-2026-0042"
TOTAL_PAGES = 3

BRAND = colors.HexColor("#1F3A5F")
LIGHT = colors.HexColor("#E8EEF5")

# The built-in PDF fonts (Helvetica etc.) have no ₹ glyph, so embed a TTF
# that does. Fall back to "Rs." if the font isn't available on this machine.
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
FONT_FILES = {
    "Body": "Georgia.ttf",
    "Body-Bold": "Georgia Bold.ttf",
    "Body-Italic": "Georgia Italic.ttf",
}
try:
    for name, file in FONT_FILES.items():
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="Body-Bold", italic="Body-Italic"
    )
    FONT, FONT_BOLD, FONT_ITALIC = "Body", "Body-Bold", "Body-Italic"
    RUPEE = "₹"
except Exception:
    FONT, FONT_BOLD, FONT_ITALIC = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
    RUPEE = "Rs. "


def inr(amount: int) -> str:
    """Format an amount with Indian digit grouping, e.g. 625000 -> ₹6,25,000."""
    s = str(amount)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return f"{RUPEE}{s}"


# --- Styles -----------------------------------------------------------------
base = getSampleStyleSheet()
styles = {
    "title": ParagraphStyle(
        "title", parent=base["Title"], fontName=FONT_BOLD, fontSize=18,
        textColor=BRAND, spaceAfter=2,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", parent=base["Normal"], fontName=FONT, fontSize=10,
        alignment=TA_CENTER, textColor=colors.grey, spaceAfter=10,
    ),
    "h1": ParagraphStyle(
        "h1", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=13,
        textColor=BRAND, spaceBefore=10, spaceAfter=4,
    ),
    "h2": ParagraphStyle(
        "h2", parent=base["Heading3"], fontName=FONT_BOLD, fontSize=10.5,
        spaceBefore=6, spaceAfter=2,
    ),
    "body": ParagraphStyle(
        "body", parent=base["Normal"], fontName=FONT, fontSize=9.5, leading=13,
        spaceAfter=4,
    ),
    "bullet": ParagraphStyle(
        "bullet", parent=base["Normal"], fontName=FONT, fontSize=9.5, leading=13,
        leftIndent=14, bulletIndent=4, spaceAfter=2,
    ),
    "cell": ParagraphStyle(
        "cell", parent=base["Normal"], fontName=FONT, fontSize=9, leading=11.5,
    ),
    "cell_bold": ParagraphStyle(
        "cell_bold", parent=base["Normal"], fontName=FONT_BOLD, fontSize=9,
        leading=11.5, textColor=colors.white,
    ),
    "note": ParagraphStyle(
        "note", parent=base["Normal"], fontName=FONT_ITALIC, fontSize=8.5,
        leading=11, textColor=colors.HexColor("#444444"), spaceBefore=4,
    ),
}


def h1(text):
    return Paragraph(text, styles["h1"])


def h2(text):
    return Paragraph(text, styles["h2"])


def p(text):
    return Paragraph(text, styles["body"])


def bullets(items):
    return [Paragraph(item, styles["bullet"], bulletText="•") for item in items]


def table(rows, col_widths, header=True):
    """Build a styled table. Cell strings are wrapped in Paragraphs."""
    data = []
    for i, row in enumerate(rows):
        style = styles["cell_bold"] if header and i == 0 else styles["cell"]
        data.append([Paragraph(str(c), style) for c in row])
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0BCCB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ]
    t.setStyle(TableStyle(cmds))
    return t


# --- Page decoration ----------------------------------------------------------
def draw_page(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(BRAND)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_BOLD, 11)
    canvas.drawString(18 * mm, h - 9 * mm, "COVEXA GENERAL")
    canvas.setFont(FONT, 9)
    canvas.drawRightString(w - 18 * mm, h - 9 * mm, f"Policy No. {POLICY_NO}")

    canvas.setFillColor(colors.grey)
    canvas.setFont(FONT, 7.5)
    canvas.drawString(
        18 * mm, 10 * mm,
        f"{COMPANY} · Fictional sample document for testing only · Not a real insurance contract",
    )
    canvas.drawRightString(w - 18 * mm, 10 * mm, f"Page {doc.page} of {TOTAL_PAGES}")
    canvas.restoreState()


# --- Content ----------------------------------------------------------------
def page_one():
    story = [
        Paragraph("Private Car Package Policy", styles["title"]),
        Paragraph(
            f"{COMPANY} · Policy Schedule and Wording · UIN: CVX-MOT-PCP-2026",
            styles["subtitle"],
        ),
        h1("Policy Schedule"),
        table(
            [
                ["Policy Number", POLICY_NO, "Period of Insurance",
                 "01-Apr-2026 to 31-Mar-2027 (both days inclusive)"],
                ["Policyholder", "Ananya R. Mehta (fictional)", "Vehicle",
                 "2023 Hyundai Creta SX 1.5 Petrol"],
                ["Registration No.", "MH-12-QX-4821", "Seating Capacity", "5"],
                ["Insured Declared Value (IDV)", inr(8_75_000), "No Claim Bonus",
                 "25% (applied to Own Damage premium)"],
                ["Compulsory Deductible", inr(2_000) + " per claim",
                 "Total Premium (incl. 18% GST)", inr(24_386)],
            ],
            col_widths=[35 * mm, 45 * mm, 40 * mm, 54 * mm],
            header=False,
        ),
        h1("Section 1 — Cover"),
        p(
            "Subject to the terms, conditions and exclusions of this Policy, Covexa "
            "General will indemnify the Insured against loss or damage to the insured "
            "vehicle and against legal liability to third parties as set out below."
        ),
        h2("1.1 Own Damage"),
        p("We will pay for loss of or damage to the insured vehicle and its accessories caused by:"),
        *bullets([
            "Fire, explosion, self-ignition or lightning.",
            "Burglary, housebreaking or theft, including theft of the entire vehicle.",
            "Riot, strike, malicious act and terrorist activity.",
            "Flood, cyclone, storm, hailstorm, earthquake, landslide or rockslide.",
            "Accidental external means, including collision and overturning.",
            "Damage in transit by road, rail, inland waterway, lift, elevator or air.",
        ]),
        h2("1.2 Liability to Third Parties"),
        p(
            "We will indemnify the Insured against legal liability for death or bodily "
            "injury to any third party without limit, and for damage to third-party "
            f"property up to {inr(7_50_000)} per accident, as required under the "
            "Motor Vehicles Act, 1988."
        ),
        h2("1.3 Personal Accident Cover for Owner-Driver"),
        p(
            f"Compulsory personal accident cover of {inr(15_00_000)} for the registered "
            "owner-driver, for death or permanent total disability resulting from an "
            "accident while driving, mounting or dismounting the insured vehicle."
        ),
        h2("1.4 Limits of Liability Summary"),
        table(
            [
                ["Cover", "Limit"],
                ["Own Damage (total loss / theft)", f"Up to IDV of {inr(8_75_000)}"],
                ["Third-party bodily injury", "Unlimited"],
                ["Third-party property damage", f"{inr(7_50_000)} per accident"],
                ["Owner-driver personal accident", inr(15_00_000)],
                ["Towing to nearest garage (accident)", f"Up to {inr(1_500)} per event"],
            ],
            col_widths=[90 * mm, 84 * mm],
        ),
    ]
    return story


def page_two():
    story = [
        h1("Section 2 — Exclusions"),
        p("Covexa General shall not be liable under this Policy for:"),
        h2("2.1 General Exclusions"),
        *bullets([
            "Any accidental loss or damage occurring outside India.",
            "Any claim arising while the vehicle is used for hire or reward, racing, "
            "pace-making, speed testing or reliability trials.",
            "Any loss while the vehicle is driven by a person who does not hold a valid "
            "driving licence, or by the Insured while under the influence of alcohol "
            "(blood alcohol above 30 mg per 100 ml) or drugs.",
            "Consequential loss, including loss of use, depreciation, and wear and tear.",
            "Loss or damage caused by war, invasion, nuclear weapons or ionising radiation.",
            "Any contractual liability.",
        ]),
        h2("2.2 Own Damage Exclusions"),
        *bullets([
            "Mechanical or electrical breakdown, failure or breakage.",
            "Damage to tyres and tubes, unless the vehicle is damaged at the same time, "
            "in which case liability is limited to 50% of the replacement cost.",
            "Depreciation on replaced parts, unless the Zero Depreciation add-on "
            "(Section 4.1) is in force.",
            "Engine damage caused by water ingress (hydrostatic lock), unless the Engine "
            "Protect add-on (Section 4.3) is in force.",
            "Loss of or damage to accessories by burglary, housebreaking or theft unless "
            "the vehicle itself is stolen at the same time.",
            "Any damage occurring while the vehicle is being driven after an accident "
            "without necessary repairs having been carried out.",
        ]),
        h1("Section 3 — Deductibles"),
        p(
            "A deductible is the portion of each admissible Own Damage claim that the "
            "Insured must bear. Deductibles do not apply to third-party liability claims."
        ),
        h2("3.1 Deductible Schedule"),
        table(
            [
                ["Deductible Type", "Amount", "Applies To"],
                ["Compulsory deductible", inr(2_000),
                 "Every Own Damage claim, regardless of claim amount"],
                ["Voluntary deductible", inr(0),
                 "Not opted for this Policy period"],
                ["Glass-only claim", inr(500),
                 "Windshield or window glass damage with no other damage"],
                ["Driver aged under 25 at time of loss", f"Additional {inr(3_000)}",
                 "Charged on top of the compulsory deductible"],
            ],
            col_widths=[52 * mm, 34 * mm, 88 * mm],
        ),
        h2("3.2 Worked Example"),
        p(
            f"The insured vehicle suffers a collision and the assessed repair cost is "
            f"{inr(42_000)}. With the Zero Depreciation add-on in force, no depreciation "
            f"is applied. The amount payable is {inr(42_000)} − {inr(2_000)} "
            f"(compulsory deductible) = <b>{inr(40_000)}</b>. If the driver had been aged "
            f"23, a further {inr(3_000)} would be deducted, making the amount payable "
            f"{inr(37_000)}."
        ),
        Paragraph(
            "Without the Zero Depreciation add-on, depreciation of 50% on rubber, nylon "
            "and plastic parts, 30% on fibreglass parts, and age-based depreciation on "
            "metal parts would be deducted before the compulsory deductible is applied.",
            styles["note"],
        ),
    ]
    return story


def page_three():
    story = [
        h1("Section 4 — Add-ons"),
        p(
            "The following optional covers apply only when shown as <b>Opted</b> below and "
            "the corresponding additional premium has been paid."
        ),
        table(
            [
                ["Add-on", "Status", "Premium", "Key Terms"],
                ["4.1 Zero Depreciation (Bumper-to-Bumper)", "Opted", inr(3_150),
                 "No depreciation deducted on replaced parts. Maximum 2 claims per "
                 "policy year. Vehicle must be under 5 years old."],
                ["4.2 Roadside Assistance", "Opted", inr(399),
                 "24x7 towing up to 50 km, flat-tyre change, battery jump-start, fuel "
                 "delivery up to 5 litres."],
                ["4.3 Engine Protect", "Opted", inr(1_120),
                 "Covers engine and gearbox damage from water ingress or oil leakage."],
                ["4.4 Return to Invoice", "Not opted", "—",
                 "Pays the gap between IDV and original invoice value on total loss or theft."],
                ["4.5 Consumables Cover", "Opted", inr(450),
                 "Covers engine oil, coolant, nuts, bolts and other consumables used in repair."],
            ],
            col_widths=[44 * mm, 20 * mm, 20 * mm, 90 * mm],
        ),
        h1("Section 5 — Claims Process"),
        h2("5.1 Steps to Make a Claim"),
        *bullets([
            "<b>Notify us immediately:</b> call 1800-000-2026 (toll-free, 24x7), email "
            "claims@covexa.example, or use the Covexa app. Quote Policy No. "
            f"{POLICY_NO}.",
            "<b>Theft or third-party injury:</b> file an FIR at the nearest police station "
            "within 24 hours and share a copy with us.",
            "<b>Do not move or repair</b> the vehicle before our surveyor inspects it, "
            "except to prevent further damage. Survey is completed within 48 hours of "
            "notification.",
            "<b>Cashless repair:</b> take the vehicle to any of 4,200+ Covexa network "
            "garages. You pay only the deductible and non-admissible items.",
            "<b>Reimbursement:</b> for non-network garages, pay the garage and submit the "
            "original bills. Approved amounts are paid within 7 working days.",
        ]),
        h2("5.2 Claim Window"),
        p(
            "<b>All claims must be reported to Covexa General within 30 days of the date "
            "of loss.</b> Claims reported after 30 days will be considered only if the "
            "Insured provides a written explanation of the delay that is acceptable to us. "
            "Supporting documents must be submitted within 30 days of claim intimation."
        ),
        h2("5.3 Documents Required"),
        *bullets([
            "Completed claim form signed by the Insured.",
            "Copy of Registration Certificate and the driver's valid driving licence.",
            "Copy of FIR (theft, third-party injury or malicious damage).",
            "Repair estimate and final invoice, with payment receipt for reimbursement claims.",
        ]),
        Spacer(1, 8),
        KeepTogether([
            p(
                f"Signed for and on behalf of <b>{COMPANY}</b>, Mumbai. "
                "Issued on 28-Mar-2026."
            ),
            Paragraph(
                "Grievances: grievance@covexa.example. If unresolved within 15 days, the "
                "Insured may approach the Insurance Ombudsman. This is a fictional document "
                "created for software testing and has no legal effect.",
                styles["note"],
            ),
        ]),
    ]
    return story


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title=f"Motor Insurance Policy {POLICY_NO}",
        author=COMPANY,
        subject="Fictional sample motor insurance policy",
    )
    story = page_one() + [PageBreak()] + page_two() + [PageBreak()] + page_three()
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)

    if doc.page != TOTAL_PAGES:
        raise SystemExit(
            f"Expected {TOTAL_PAGES} pages but got {doc.page}; content overflowed a page."
        )
    print(f"Wrote {OUT} ({doc.page} pages)")


if __name__ == "__main__":
    build()

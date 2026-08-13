# OZR Generation Rules and Constraints

These rules have been established from previous tuning sessions to achieve a 98% structural sync rate with PLA0501_R25.

1. **A4 Boundary Constraints (Y_SCALE_FACTOR)**:
   - Do NOT artificially inflate the Y-axis heights of the generated rows.
   - The `Y_SCALE_FACTOR` should remain at 1.0 (or very close to it) to prevent the total height from exceeding the A4 boundary (max height should remain around 80.5-84.0 to match R25).
   
2. **Missing Dataset Tag Mappings**:
   - If a source Excel template lacks explicit `<DATASET:COLNAME>` markers, the missing fields must be manually mapped or hardcoded (e.g., mapping `COL1` to `DOC_NO`, `COL2` to `REV_NO`) for the `TR_VIEW` dataset to match the human-generated R25 structure perfectly.
   
3. **Repeating Rows Collapse**:
   - The user's Excel files often contain redundant mock data rows (e.g., rows 12~30).
   - Use the implemented grid similarity check (checking `min_x`, `max_x` of cells) to group these identical repeating rows into a single `<OZDATABAND>` structure rather than creating hundreds of redundant `<OZTABLELABEL>` tags.
   
4. **XML Tag Consistency**:
   - Empty tags must match the behavior of OZ Report Designer (e.g., using self-closing tags `/>` for `OZGROUPLABEL` when no text is explicitly populated).

5. **Sync Score Targeting**:
   - For any future parser logic updates, benchmark the output against `PLA0501_R25.ozr` (using `scoring.py`). Ensure the sync rate remains above 90%.

6. **Text Formatting & Single-Line Layout Constraints**:
   - Refer to [.agents/skills/ozSkill/SKILL.md](file:///d:/DEV/oz/.agents/skills/ozSkill/SKILL.md).
   - Set `AUTOFONTSIZE="smallerOnly"`, `WORDWRAP="false"`, `AUTOSIZE="false"` on data cells (`OZGROUPLABEL`) to prevent text overflow and unwanted multi-line wrapping.
   - Preserve 2pt internal margins (`LEFTMARGIN="2" RIGHTMARGIN="2"`).
   - Map `HALIGN` (0=Left, 1=Center, 2=Right) and `VALIGN` (0=Top, 1=Center, 2=Bottom) correctly from source Excel cell alignments.

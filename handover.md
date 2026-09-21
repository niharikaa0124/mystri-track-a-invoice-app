# Track A — Product Engineering Handover

**Track:** A — Product Engineering

**Repository:** https://github.com/niharikaa0124/mystri-track-a-invoice-app

---

## 1. What I Worked On

I repaired the existing invoice application while keeping the existing register data intact.

My approach was:

1. Understand the existing application flow and business rules.
2. Reproduce the reported issues before changing the code.
3. Identify the root cause of each issue.
4. Make focused changes without unnecessarily restructuring the application.
5. Add regression tests for the fixed behaviour and edge cases.
6. Verify the changes through both automated tests and the running web application.
7. Restore and verify the original register data before finalising the submission.
8. Add a small product improvement to make CSV imports more informative to users.

---

## 2. Bugs Fixed

### Payment Matching

**Issue:** The original payment matching logic could match a payment to an invoice based on the payment amount alone, before confirming the invoice identity. This could incorrectly associate an unrelated payment with an invoice that happened to have the same amount.

**Fix:** Payment matching now uses the invoice identity — customer ID + invoice number — instead of amount.

**Verification:** Reproduced the incorrect match using a payment with a fake customer/invoice identity and confirmed the corrected implementation returns no match. Also verified that a valid invoice identity still matches correctly even when the payment amount differs.

### Duplicate Invoice Handling

**Issue:** The application previously allowed duplicate invoices to be inserted.

**Fix:** Added duplicate handling based on `customer_id + invoice_number`:

- Identical duplicate → skipped safely.
- Same identity with different invoice details → rejected.
- New invoice → imported normally.

This prevents duplicate records while avoiding silent acceptance of conflicting data.

### Open / Paid Invoice Filtering

**Issue:** The existing open and paid filters were returning incorrect results because the filtering logic mapped the requested status incorrectly.

**Fix:** Corrected the reporting logic so that:

- `all` → all invoices
- `open` → only open invoices
- `paid` → only paid invoices

Regression tests were added for both filtered states.

### Money Formatting

**Issue:** The CSV export previously used floating-point truncation when formatting monetary values.

**Fix:** Changed the formatting to use `Decimal` with two-decimal rounding, avoiding incorrect monetary values caused by floating-point representation and ensuring exported amounts are consistently represented to two decimal places.

### Frontend Import Error Handling

**Issue:** The frontend previously ignored the HTTP status returned by the import API. As a result, a failed request could still display "Import complete. Your records are ready."

**Fix:** The frontend now checks the HTTP response and displays the actual backend error when an import request fails.

### Partial CSV Row Validation

**Issue:** A single invalid row in a CSV should not prevent valid rows from being processed.

**Fix:** Updated the import flow so that:

- Valid rows continue importing.
- Invalid rows are rejected individually.
- The import continues after a rejected row.
- The response reports the rejected row's line number and reason.

**Example from browser verification:**

`Import complete. Imported: 2 · Skipped: 0 · Rejected: 1 · Line 3: amount must be a positive decimal with at most two decimal places`

This gives users immediate visibility into what happened during a bulk import and makes data-quality issues easier to correct.

---
## 3. Product Improvement

### Import Result Summary

As the useful improvement, I added a detailed import summary to the UI.

Instead of showing only a generic success message, the application now reports:

- Number of imported records
- Number of skipped records
- Number of rejected records
- Line number of rejected records
- Reason for rejection

Example:

`Import complete. Imported: 2 · Skipped: 0 · Rejected: 1 · Line 3: amount must be a positive decimal with at most two decimal places`

This gives users immediate visibility into what happened during a bulk import and makes data-quality issues easier to correct.

---

## 4. Testing and Verification

Regression tests were added covering the repaired behaviour, including:

- Payment identity matching
- Duplicate invoice handling
- Conflicting duplicate invoices
- Open invoice filtering
- Paid invoice filtering
- Invalid-row handling during CSV import

The complete test suite was run using:

```bash
python -m unittest discover -s tests -v
```

**Result:** 10 tests passed.

The application was also verified through the browser rather than relying only on unit tests.



## 5. Data Preservation

The existing register was restored after testing and verified before finalising the submission.

**Final database verification:**

- Invoices: 9
- Payments: 5

The local working database is excluded from the Git repository through `.gitignore`. The original assessment fixture remains available at `fixtures/existing-register.sqlite3` and was restored to its original state before submission.

---

## 6. Verification Approach

Passing tests alone were not treated as sufficient verification. For the important fixes, multiple levels of verification were used:

- **Code-level verification** — Inspected the existing implementation and traced the relevant application flow.
- **Reproduction** — Reproduced incorrect behaviour before fixing it, including the incorrect payment-to-invoice match.
- **Regression testing** — Added automated tests so the bugs cannot silently return.
- **Application verification** — Started the application and tested CSV imports through the actual browser UI.
- **Data verification** — Checked the final invoice and payment counts after restoring the register.
- **Final repository check** — Verified that local databases, backups, Python cache files, and environment files were excluded from the repository.

---

## 7. Engineering Decisions

Changes were intentionally kept focused on the existing architecture rather than rewriting working parts of the application.

For example, instead of changing the overall import architecture, row-level validation was handled inside the existing import flow so valid records could continue processing while invalid records were reported.

For duplicate invoices, I chose to distinguish between an identical duplicate and a conflicting duplicate rather than silently ignoring both cases. This prevents duplicate records while still exposing potentially inconsistent source data.

---

## 8. AI-Assisted Development

**AI assistant:** ChatGPT  
**Model:** GPT-5.6 Luna  
**Configuration:** Instant

AI assistance was used for codebase understanding, debugging, identifying edge cases, suggesting implementation approaches, and drafting regression tests.

AI-generated suggestions were independently reviewed and verified. I reproduced the relevant issues, inspected the affected source code, applied the appropriate changes, ran the regression test suite, and verified the behaviour through the running application.

One concrete issue identified during verification was the payment-matching bug: matching by amount could associate an unrelated payment with an invoice. I reproduced this behaviour and changed the matching logic to use the actual invoice identity (customer ID + invoice number).

I also identified a stale application/browser state during frontend verification. After restarting the application and performing a hard refresh, I repeated the test and confirmed the corrected behaviour.

---

## 9. Final Outcome

The repaired application now:

- Matches payments using invoice identity.
- Prevents duplicate invoice records.
- Rejects conflicting duplicate data.
- Correctly filters open and paid invoices.
- Handles monetary values using proper decimal rounding.
- Reports HTTP import failures correctly.
- Continues processing valid CSV rows when another row is invalid.
- Provides users with a clear import summary.
- Includes regression coverage for the repaired behaviour.
- Preserves the existing register data.

**Final verification:** 10 automated tests passed, and the restored register was verified with 9 invoices and 5 payments.

The final implementation is available in the GitHub repository linked above.
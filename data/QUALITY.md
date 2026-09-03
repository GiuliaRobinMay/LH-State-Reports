# Source data quality

Harvested from 52 states/territories and 311 linked documents in the master Google Doc.
Parsed into **9,649 programs** and **18,003 links**.

Everything below is a defect in the original Drive folder, not in the extraction. The app still shows the original Google Doc link for every report, so nothing is lost to the reader.

## Documents that could not be fetched

The linked file returns *"Requested entity was not found"* — it has been deleted, or it is not shared with the account that ran the harvest. These categories appear in the app with the original link and no programs.

| State | Report | Link |
|---|---|---|
| Alabama | Financial Assistance | [source](https://docs.google.com/document/d/1PFFt1NDZTyTkip4cfxoKjw6b6sfnDJnUaMesQbNA4U8/edit?usp=sharing) |
| Alabama | Jobs, Education, Training | [source](https://docs.google.com/document/d/1ZK3q_qYl_e-kR6k9zgmKWXOJgpvIiePhJQPLS4SZils/edit?usp=sharing) |
| Alaska | Jobs, Education, Training | [source](https://docs.google.com/document/d/16Wqg40RH57Kn9S9t9VAvOvFE6Th0ANzIZyOGeWqBbR8/edit?usp=sharing) |
| California | Jobs, Education, Training | [source](https://docs.google.com/document/d/18L_oAsoykZwRfnpPNmV-zsSXeEfrvxRG1EPnT1Q32ps/edit?usp=sharing) |
| Idaho | Jobs, Education, Training | [source](https://docs.google.com/document/d/1zgenj56xyoO662POXRKd6o2yKUvWHF3dpdd4DuosjZI/edit?usp=sharing) |
| Kansas | Jobs, Education, Training | [source](https://docs.google.com/document/d/11fHsqBLku3W5pVx9OpfDv8OA6cUVhXPeoRkxZUnFC8o/edit?usp=sharing) |
| Kentucky | Financial Assistance | [source](https://docs.google.com/document/d/1JfQpPCTZ2iuagI5QRvxCUnPmOxJ2uG5_P1K5pZFCUSM/edit?usp=sharing) |
| Maryland | Jobs, Education, Training | [source](https://docs.google.com/document/d/1MmcWlR16XX9gcDRb-ZtTVEK4VQ51icKtwva4UXiACk8/edit?usp=sharing) |
| Montana | Free Local Mentoring, Consulting, and Research Help | [source](https://drive.google.com/file/d/1dAnvTSNRz3umMnaDjbBbbUf0nXH3juO1/view?usp=sharing) |
| North Dakota | Jobs, Education, Training | [source](https://docs.google.com/document/d/1TmvNdqaJpBocNIqNGf-K8X-X-LB1SJAiCc0LeqTmZ6g/edit?usp=sharing) |
| Ohio | Jobs, Education, Training | [source](https://docs.google.com/document/d/1zEP7uBVC4rvkGQ_9wisJnNGjtejCi6mbNtFh5V4gpn0/edit?usp=sharing) |
| Ohio | Free Local Mentoring, Consulting, and Research Help | [source](https://drive.google.com/file/d/17cdzovseL5xFfQzTE8GxJ-rqMDiaKEK3/view?usp=sharing) |
| Oklahoma | Jobs, Education, Training | [source](https://docs.google.com/document/d/1xBWtQUteW_r9G_uKm20ntF6ajQR_vZu_2uQfb5S2tXs/edit?usp=sharing) |
| Pennsylvania | Jobs, Education, Training | [source](https://docs.google.com/document/d/1KJsaUapDeeqDu5pm0g1hp8goTp7fKGTyfJg0blSlvhI/edit?usp=sharing) |
| Virginia | Jobs, Education, Training | [source](https://docs.google.com/document/d/1lkucRg5KvLHh0Z2lKHeNR-lSzBq59rlQNEnrwC1XYZM/edit?usp=sharing) |
| Washington | Jobs, Education, Training | [source](https://docs.google.com/document/d/1TKeOP3x-D2yGPvBAyA0IiV3FCFr0JQilhppRC7lDk10/edit?usp=sharing) |
| West Virginia | Jobs, Education, Training | [source](https://docs.google.com/document/d/126bHeczQJuZKZrDVcLYSgH0ix200cVXCKYsYbVefQHU/edit?usp=sharing) |
| Wisconsin | Jobs, Education, Training | [source](https://docs.google.com/document/d/1JsBSPGRkrHCxkN7NpCBucYS6-0A8KP1T8K9dLPJHFFE/edit?usp=sharing) |
| Wyoming | Jobs, Education, Training | [source](https://docs.google.com/document/d/1zFjEzPAII7nbwWQmIrkOMQIwyg6VMT9IpCBIMAfNSRs/edit?usp=sharing) |
| Wyoming | Real Estate and Housing | [source](https://drive.google.com/file/d/1Nk6A4QqhTtcjfRrzOqdyhlPSBZgxIBq-/view?usp=sharing) |

## Documents that are effectively empty

The document exists and was fetched, but the source itself has almost no content.

| State | Report | Characters | Link |
|---|---|---|---|
| Delaware | Financial Assistance | 124 | [source](https://docs.google.com/document/d/1fl90Bko9_vdFCgHcU88WKXuot9HHWY4jBPixkYcS8HI/edit?usp=sharing) |
| Utah | Financial Assistance | 316 | [source](https://docs.google.com/document/d/1q33bSn2U8h7L6M0GeGSz83FzzAd4UhBdoK5qEjcpWzQ/edit?usp=sharing) |

## Known defects inside the source documents

Found while parsing. All content is preserved verbatim in `raw/docs/`; none of these were "fixed", because guessing at the author's intent would be worse than showing what he wrote.

- **Copy-paste headings from the wrong state.** Michigan and New Jersey housing reports carry the heading *"HUD Identified Programs for Homeownership In Alaska"*, though the link underneath is correct for the state. California's dental section is headed *"Free and Low-Cost Dental Clinics in New Jersey"*. Arizona's financial report links `211connectsalabama.org` beside the correct `211arizona.org`. North Carolina's jobs report opens with the heading *"Arizona"*. Several "Biz Done" reports (Tennessee, Utah, Virginia, Wyoming) open with *"Why does Indiana want to help you…"*.
- **One misassigned link.** The master document's North Carolina *Financial Assistance* link points at a Google Doc titled "Book notes" — a short personal outline, not a Lesko report.
- **Editing debris.** A few documents contain stray characters left over from editing (a run of backslashes in Oregon, `Aa as à AA qàáà see em` in Virginia, empty "Tab 2/3/4" sections in several). The parser drops single-character and separator-only lines, so most of this never reaches the app.
- **Duplicated sections.** Delaware and Virginia are listed twice in the master document with two different sets of six links; both sets are merged into one entry per state. Puerto Rico is listed with two *Jobs, Education, Training* links and no *Financial Assistance* or *Health* report.
- **Dead external links.** Many programs point at pages that have moved since the reports were written (`youcaring.com` shut down, several `hud.gov` and `portal.hud.gov` paths now redirect). Link-checking is a separate pass and has not been run.

## Categories with no programs in the app

These are the consequence of the two lists above.

Alabama (financial), Alabama (jobs), Alaska (jobs), California (jobs), Delaware (financial), Idaho (jobs), Kansas (jobs), Kentucky (financial), Maryland (jobs), Montana (mentoring), North Carolina (financial), North Dakota (jobs), Ohio (jobs), Ohio (mentoring), Oklahoma (jobs), Pennsylvania (jobs), Utah (financial), Virginia (jobs), Washington (jobs), West Virginia (jobs), Wisconsin (jobs), Wyoming (jobs), Wyoming (housing)

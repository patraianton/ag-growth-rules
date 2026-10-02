# Review of the fix pass, 2026-10-02 · model: Fable (Anthropic, the same family as the writers)

Read (09:12-09:18): the kit as the fix pass left it, `kit.md` sha256 `b6ca08ccc9b684a3a210320f1f57c9b3efb41098a5eed52b3e592ac1bd444e4e`,
the diff against the 2026-10-01 version, and the repository changes. That text was not kept as a file; its
hash is the one the checker printed when the next step opened (exit 0).
Not read: `after.txt` (sha256 7a990378...), which is that text with the four blockers below fixed, and the
released text (sha256 368ca8d1...), which came after it (how-made rewrite, "Quotes" table row).

Blockers: 4. A separate step (09:18-09:19, agent, Anthropic model) applied the four suggested fixes word for
word to `kit.md` and `index.html`; the checker then wrote `after.txt` (sha256 7a990378..., exit 0). In
`templates/decisions.md` they are E-08 to E-11. As returned (line numbers are the reviewed version's):

1. kit.md:150, section 4, the IMO note's compliance paragraph: "For your compliance team: texting consent,
   opt-outs, call recording and how long messages are kept are open questions, and we'd like to settle them
   with you before your agents' email goes out." Problem: editor's to-confirm language leaked into customer
   copy; a vendor note to IMO compliance a week before launch says its own compliance rules "are open
   questions". Fix: "For your compliance team: we'd like to walk through texting consent, opt-outs, call
   recording and message retention with you before your agents' email goes out. Your firm's policies still
   apply." (E-08)
2. kit.md:161, How this was made, intro: "...a fact-checker), one model family on one research folder, with
   fixes applied between rounds; this version has changed since." Problem: a dangling phrase that attaches
   to nothing. Fix: "...a fact-checker) - all from one model family, all reading the same research folder -
   with fixes applied between rounds. This version has changed since. Sources are linked or listed below."
   (E-09; the paragraph was rewritten again later, E-07)
3. kit.md:42-45, section 1, "You stay in control" bullet 3: "- Texting rules and your data: ask us anything
   at Wednesday's live Q&A." Problem: under a heading that promises control, the bullet defers the answer.
   Fix: delete the bullet; after the webinar line add "Bring your questions on texting rules and your data -
   the live Q&A is for them." (E-10)
4. kit.md:95, section 2, side note "Format": "Pain above the fold (LinkedIn cuts after about three lines)."
   Problem: a new fact with no research source. Fix: "Pain in the first two lines. Margaret is an invented
   client." (E-11)

The blocker text above was recovered on 2026-10-02 from the record of the run's agent steps; the first
version of this file said it had not been kept, and said Fable read `after.txt`. Both were wrong.

Minor notes, as returned (line numbers are the reviewed version's):

1. kit.md:63 side note 5: "the time to move an existing one is to confirm" is a note-to-self shape inside a full-sentence note. Suggested: "Calling starts with a new local number; how long moving an existing one takes is on the To confirm list." (checker exit 0). Status: open.
2. kit.md:213 (To confirm, 'Promises AG would be making: questions...'): the one statement among questions, "The agents' launch email can go out co-signed by the IMO, or be handed to the IMO to send." Suggested question form: "Co-signed send: will AG send the agents' launch email co-signed by an IMO, or hand the IMO the copy to send?" (checker exit 0). Status: open (decision row D-14).
3. (d) tools/check.py check_repeats URL blanking: real false positive (two markdown links to sibling pages on patraianton.github.io shared an 8-word run of host/path tokens); same blanking check_voice already uses; fixture mn-21 added; selftest 158 fixtures 0 failed. Not a loosening.
4. (d) templates/numbers.json N-17..N-23 verified against ghl-complaints-2026-10-01.md lines 44-58 (271/216/210/168/147/92/50, all approximate with the double-count caveat); N-24 verified against crm-module-brief-2026-09-30.md line 267 ('up to 5 business days', Twilio). Not a loosening.
5. (d) templates/claims.csv: CL-05/CL-06 removal is legitimate (both sentences are gone from the kit), but the ledger now has zero TO-CONFIRM rows while the kit carries about nine bracketed to-confirm items (from your own number; from the agent's own number; pick the emails and call notes; bring your office line over; Team Activity; agency switch; co-signed email; both offers; Novak slot). The claims check is green by absence of rows, not by coverage. Known limit; needs an AG owner before rows can be added without failing. Status: rows added after this review as PROPOSAL (CL-03 to CL-19), each naming its open decision row; see the run README, "Claims ledger".
6. templates/decisions.md is stale: killed-lines 'came back' column still cites kit.md lines 42/50/70 for K-01/K-02/K-06 (lines now gone, checker killed-lines passes); release record says '"four review rounds" on the page' (the page no longer says that) and lists the pre-edit sha256. Documentation only. Status: fixed after this review (E-01, release record).
7. (a) Nothing required by the brief was lost: email, social post, webinar agenda all present; six parts visible (emails/calls/texts/meetings in email bullets 1-2 and the post; quotes in 'The message', the post's first line and webinar 0:07; E-Apps in the timeline bullet, the post and webinar 0:17). Cutting 'The bet' paragraph removed the one line about GoHighLevel's place in the launch; GoHighLevel is now addressed in how-made step 2, the six-row table and questions 3-4.
8. (c) Verified as sourced: 'until now, texting was for website leads only' (crm-features-audit line 124 recommends this exact wording); 'September 29 post opened with "New in Annuities Genius:"' (style guide line 230); 'from Lead to Close' (style guide line 314); February 13, 2026 webinar quote (audit line 51); Google yearly security assessment 'several weeks' (module brief line 287); (225) 535-4832 shared number (audit line 21); 2,721 followers on the page (module brief line 353); 3,803 records / 1,927 complaints / eight source types (ghl-complaints lines 11, 37, 44); 98 IMO sites (imo-interview-brief line 114); 'AG has no app at all' (audit line 111); 'Client Management left Starter in June 2026' and texting on mid/upper plans 2023-2025 (audit lines 25, 102); 'support and billing are 30%' = (309+271)/1927; Danny/Oleg/Novak roles (style guide lines 298-300); 949-600-7707 and FireLight (audit line 137).
9. All four blocker fixes were tested together on a temp copy: tools/check.py exit 0 (landmines, voice, numbers, repeats, time-promises, claims, mark-budget, killed-lines pass). Parity was not run on the temp copy; every change must be applied to index.html too or parity will fail. Status: parity passes on `after.txt` and on the release run.

# Plain pass: the prompt (`process/LINE.md` step 4½)

You get the piece, `rules/landmines/plain-language.md`, the AG terms in `rules/voice.md` section 8 and the
`plain` lines of `tools/check.py`. Rewrite only the language. One idea per sentence, AG's words, no new facts,
hook untouched (the email's first paragraph after the greeting), quoted speech untouched.

1. F1: a sentence over 20 words becomes two or three sentences.
2. F2: a list item with a semicolon, two dash asides, or more than three long sentences is split or cut down.
3. F3: a 3-word phrase said three times in one item or paragraph is said once.
4. F4: a term that is not AG's and not plain English gets plain words in the same sentence; a heading with an
   AG term also says it in plain words.
5. F5: a side-note title is a full sentence or a plain noun phrase: no "=", no "X, not Y", no "line".
6. F6: the email body and the IMO note read at grade 9 or lower, the how-made steps at grade 11 or lower.
7. F7: "until now", "as before", "because", "so that" leave the feature sentence for a side note.

Keep every fact, number, name and bracketed or dotted mark; a history remark moves to a side note, it does
not vanish. Do not restructure, add or cut. Change the page the same way (parity). Write the list as
`was → now`, one line per changed sentence, in `plain-pass.md` in the run folder (`process/runs/<run>/`). Done when check `plain` is 0.

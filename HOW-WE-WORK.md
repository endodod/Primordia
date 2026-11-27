# How we work 🧬

The short version. The long version is `DEV.md`. Read this one at least.

## The deal

**You own what you ship.** Claude writes a lot of our code — doesn't matter. If your name is on
the PR, it's yours. "Claude did it" is not a thing anyone gets to say.

**If you break it, it's on you — and you fix it.** No hiding, no waiting for someone else to
notice. Broke `dev`? That's your job today. Approved something broken? You share the blame —
you were the second pair of eyes.

**Owning it ≠ drama.** Mess up → say it in chat → fix it → write down what happened so nobody
does it again. That's it. Covering it up is the only real crime.

## The rules

1. **No issue, no work.** Run `/next-ticket`, claim it (you get assigned), then start. Assigned = taken.
2. **Never push to `main` or `dev`.** Branch, PR, review. Always.
3. **Read your own diff before asking for review.** Every line. If you can't explain it, it
   doesn't go in.
4. **Small PRs.** If nobody wants to review it, it's too big.
5. **You merge your own PRs on `dev`** — after CI is green and you've read the diff. Risky
   stuff (engine, run files, leaderboard, CI) waits for a teammate's approval. No exceptions.
6. **Review others within 48h.** Reviews are part of the job, not a favor. Don't approve stuff
   you didn't actually look at.
7. **Red CI is not optional.** Fix it, don't re-run it and pray.
8. **Don't break determinism.** Same run = same result, everywhere. If you touch the engine,
   you test it. If you don't understand why this matters, ask before touching the engine.
9. **Don't break old run files.** Format change = version bump + migration.
10. **Secrets never go in the repo.** Leaked one? Tell us immediately, rotate it.
11. **Update the docs** when you change how something works.

## Being a good teammate

- **Blocked? Say it.** Behind? Say it. Changing direction? Say it. Early, not on deadline day.
- **Don't ghost.** If you can't do your issue, unassign yourself and tell the group.
- **Show up** to check-ins and demos — even with nothing finished.
- **Playtest.** Actually run the thing. Watch your blobs. File issues for what sucks.
- **Write your devlog post** when it's your turn. In your words, not Claude's.
- **Big ideas → talk first.** New tech, new feature, big refactor → chat or ADR before code.
- **Leave it cleaner than you found it.**

## Who decides what

- **Your issue, your call** on the details — within the rules and ADRs.
- **Your area, you're the owner** — you review its PRs and know it best.
- **Architecture, scope, priorities → the group decides.**
- **Rules annoying?** Open a PR to change them. Until it's merged, they apply.

That's it. Build cool stuff, own your work, don't be weird about mistakes. 🦠➡️🦖

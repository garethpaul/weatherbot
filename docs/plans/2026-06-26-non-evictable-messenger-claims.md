# Non-Evictable Messenger Claims Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Prevent a concurrent Messenger retry from reclaiming a message ID while its original Wit action is still running.

**Architecture:** Split replay ownership into a non-evictable in-flight set and a bounded ordered history of completed message IDs. Successful actions move their exact claim into completed history; failed actions release only the in-flight claim so Messenger can retry.

**Tech Stack:** Python 3 standard library, Bottle/WebTest route tests, dependency-free portable contracts, GNU Make.

---

Status: Completed

### Task 1: Lock the concurrency regression

**Files:**
- Modify: `test_messenger.py`
- Modify: `scripts/check_weatherbot_contracts.py`

**Step 1: Write the failing tests**

Add native and dependency-free tests proving that completed-history rotation
cannot evict an in-flight claim and that completed IDs remain bounded.

**Step 2: Run tests to verify they fail**

Run: `python3 -m unittest test_messenger.TestMessenger.test_recent_message_ids_never_evict_in_flight_claim -v`

Expected: FAIL because the current single `OrderedDict` evicts `mid-in-flight`.

Run: `python3 scripts/check_weatherbot_contracts.py`

Expected: FAIL on the equivalent portable replay-ownership contract.

### Task 2: Separate active and completed ownership

**Files:**
- Modify: `messenger.py`

**Step 1: Implement the minimal ownership model**

Store active claims in `_in_flight`, completed IDs in `_completed`, add a
`complete(message_id)` transition, and evict only the oldest completed ID.

**Step 2: Complete successful webhook actions**

Call `recent_messenger_message_ids.complete(message_id)` immediately after a
successful `client.run_actions` return. Preserve failure release behavior.

**Step 3: Run focused tests**

Run: `python3 -m unittest test_messenger.TestMessenger.test_recent_message_ids_never_evict_in_flight_claim test_messenger.TestMessenger.test_recent_message_ids_bound_completed_history -v`

Expected: PASS.

### Task 3: Preserve maintained contracts

**Files:**
- Modify: `AGENTS.md`
- Modify: `CHANGES.md`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `scripts/check_weatherbot_contracts.py`

**Step 1: Update source contracts and guidance**

Require the split stores and success transition, and document that active
claims are never evicted while completed replay history remains bounded.

**Step 2: Run the canonical gate**

Run: `make check`

Expected: all dependency-free contracts, native route tests, Make authority
tests, syntax checks, and repository hygiene checks pass.

Observed: root and external `make check` pass with 63 dependency-free contracts
and 45 native Bottle/WebTest tests in a temporary environment installed from
the reviewed Python 3.14 hash-locked dependency graph. Hosted Python 3.10 and
3.12 remain required cross-version evidence.

**Step 3: Publish one focused commit**

Run: `git add AGENTS.md CHANGES.md README.md SECURITY.md messenger.py test_messenger.py scripts/check_weatherbot_contracts.py docs/plans/2026-06-26-non-evictable-messenger-claims.md && git commit -m "fix: preserve in-flight Messenger claims"`

# Step 6 – Customer complaint analysis with Cortex AI

**Goal:** hear the customer's voice at scale.

## Prompt

```text
Select Whitefield-East support chats from 8 Sep 2026 onward (join chats to orders and zones).

Check that my role can call AI_CLASSIFY and AI_SUMMARIZE_AGG.
Classify each message with AI_CLASSIFY into exactly these labels:
'Rider assigned too far away', 'Food arrived cold', 'General late delivery',
'Missing or wrong item', 'Food quality'
Save the results to QUICKBITE_DB.ANALYTICS.WFE_CHAT_CLASSIFIED (ask for approval first).

Show the total chats, count and % per theme, and example messages.
Then run AI_SUMMARIZE_AGG over the same messages, save it to
QUICKBITE_DB.ANALYTICS.WFE_CHAT_SUMMARY, and describe the recurring problems.
```

## Checkpoint

- About 446 chats.
- Top theme: "Rider assigned too far away", about 237 chats.
- The summary mentions far-away riders, long waits, cold food and rain.

> Pitfall: adding long descriptions to the category labels changes the distribution noticeably. Plain labels reproduce the lab checkpoint.

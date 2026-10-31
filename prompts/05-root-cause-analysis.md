# Step 5 – Root cause and weather

**Goal:** explain *why* Whitefield-East deteriorated.

## Prompt

```text
Inspect APP_RELEASES and identify releases around early September 2026.

Compare Whitefield-East with all other zones, before and after 8 Sep 2026:
- average RIDER_ASSIGN_DISTANCE_KM
- average pickup waiting time (ACCEPTED_AT -> PICKED_UP_AT, minutes)
- late-delivery % where late = DATEDIFF('minute', PLACED_AT, DELIVERED_AT) > 45

Then join WEATHER_HOURLY on CITY and DATE_TRUNC('hour', PLACED_AT).
Treat RAIN_MM > 0 as a rainy hour. Compare late % and refund rate for rainy vs dry hours,
focusing on Whitefield-East after 8 Sep. Be careful not to claim more causation than the
data supports.
```

## Checkpoint

- **Release:** rider-assign v2.3 on 2026-09-08, which "Expanded assignment radius to 10 km".
- **Whitefield-East assignment distance:** about 2.1 km before, about 6.0 km after.
- **Whitefield-East late deliveries:** about 6% before, 20–28% after. Other zones stay at about 6%.
- **Whitefield-East after 8 Sep, by weather:** rainy hours about 56% late; dry hours about 14% late.

> Pitfall: `DATEDIFF('second', …) > 2700` gives late % about 1 point higher than the minute-based definition.

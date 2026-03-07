Subject: Re: Recent Contract Launch- Deep Dive SP-OR-2626

Hey Joe,

Thanks for taking the time to do this deep dive! You were spot on with the sniff test, and it actually helped us catch a major bug in how the pipeline was rolling up the data. Keep these coming—it is incredibly helpful for us to hunt down these edge cases and tighten up the logic.

To explain what happened in simple terms: the pipeline looks at those items in Tab C and checks if there’s a matching benchmark in the database. Initially, it was just checking if the catalog numbers matched to say "Yes, this is benchmarked." However, some of those items matched a row but had a benchmark price of $0. 

Because we let those $0 benchmark items into the summary in Tab B, their actual contract spend was being added to the contract's total spend, but they were adding exactly $0 to the "Benchmark Target" side of the equation. This heavily inflated the contract's reported spend versus the benchmark, shoving **SP-OR-2626** falsely into the `<25th` bucket! 

I've pushed a fix that strictly forces any `$0` benchmark item to be ignored in the rollup mapping. Now, SP-OR-2626 only aggregates the 11 truly matched items and rightly lands in the **"Best in Market"** bucket! 

Even better, resolving this issue had an incredible impact on our overall portfolio numbers in Tab A. By filtering out these false zero-benchmarks, all the final weighted averages improved significantly:
- **Surpass:** Jumped from 68th to **74th Percentile** 
- **Ascend Drive:** Jumped from 53rd to **61st Percentile**
- **National:** Jumped from 46th to **54th Percentile**

I actually took another pass acting like a Contract Director to see if anything else "failed the sniff test". I realized that on a few big contracts (like **PP-CA-659**), our system only had the absolute worst "Tier 1 - No Commitment" pricing data available, but facilities were actually receiving prices at half that cost. Because our pipeline was benchmarking the terrible $26k "Best Tier" price against a $12k market benchmark on millions in spend, it made the contract look uncompetitive ($34M vs $15M). I patched the pipeline to identify and remove items from the benchmark where the actual average paid transaction price is radically disconnected (> 1.5x difference) from our internal definition of the "Best Tier". This successfully stripped out those false negatives and keeps the model pure.

Regarding your point #3 on shifting more weight to recently launched contracts: I definitely get where you're going and agree that recency matters for Sourcing. However, given we are looking at a 6-month historical window, contracts launched just in the past few months haven't accumulated enough total spend to dramatically move the needle on these overall weighted averages yet. When we transition to providing this data as an actionable tool for Sourcing teams, we 100% want to push the latest contract versions in each category. But for this retrospective analysis, the current volume-weighted approach gives us the most accurate snapshot of the state of things today.

Let me know if you spot anything else! I've attached the repaired and updated workbook.

Best,
Matt
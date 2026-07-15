# Evaluation — LANShare

## Benchmark method

> 

We tested semantic search quality manually: a small set of sample files (notes, PDFs) covering distinct topics was shared across two devices, and a set of natural-language queries was run against the combined index to check whether the top-ranked result was actually the most relevant file.

## Test files used



| File | 
|---|
| Space and time complexity.pdf| 
| Workout plan.pdf| 
| OOPSNotes.pdf| 

## Example queries and results



| Query | Top result | Correct match? |
|---|---|---|
| "space complexity" |Space and time complexity.pdf | Yes |
| "Lat pull down" |Workout plan.pdf | Yes|
| "advantages of oops" |OOPSNotes.pdf |Yes |

## Accuracy / quality summary



Out of `3` test queries, `3` returned the correct file as the top result, and `3` returned it within the top 3 results.

## Baseline comparison

A simple keyword/filename-match search was used as an informal baseline: searching for the same queries using plain substring matching against filenames only. Semantic search correctly surfaced relevant files even when the query didn't share any words with the filename (e.g., "___" matched "___" despite no literal keyword overlap) — this is the core improvement semantic search provides over the baseline.

## Known failure cases



- Very short files (a few words) sometimes produce embeddings that don't rank meaningfully, since there isn't enough text for the model to capture distinct meaning.
- Files with extracted text that failed (e.g., a PDF where `PyPDF2` couldn't extract text, such as a scanned/image-only PDF) fall back to filename-only matching.
- Extremely similar files (e.g., near-duplicate notes) can be hard to distinguish by ranking alone.

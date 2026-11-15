# Aggressive caching — Flashcards
Tags: #flashcards #ai-engineering #finops #caching #costs #llm
Verified on: 17 October 2026 — This page lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: prompt caching (TTL, write and read prices), stable prompt structure, which breaks the cache, append-only context, parallel requests and pre-heating, response caches, embeddings and tool caches, prompt caching, exact or semantic cache, invalidation, security, steering, false semantic cache equivalents, stampede, verified freshness. -->


What is aggressive caching for a LLM application? <!--anki:48792f4f3f4d7031763c-->
?
Reuse **a still valid and authorized job**: KV prefixes, answers, embeddings or tool results. Choose each cache according to the calculation avoided, the reuse frequency and the cost of storage and invalidation.

The best hit rate is not necessarily the best cost per hit: frequent small hits can save less than a rare heavy calculation. Measure net economy, latency and quality. Do not keep outdated or prohibited data to protect the hit rate; correction remains a condition for re-use.

---

Why do agents benefit so much from prompt caching? <!--anki:7a26753c6f77592c2f51-->
?
Agents can return **a long history and stable instructions every turn**. Reusing eligible prefixes avoids a portion of the prefill and can reduce billing depending on the provider.

The benefit depends on the actual identical tokens, cache alignment, cache lifetime, and pricing. New tool results and output still need to be processed; suffixes still read prefix states. Measure tokens re-used, written, and new, as well as TTFT, especially in the first round and after compaction. Stable context does not guarantee a full hit.

---

How does prompt caching work at Anthropic? <!--anki:653e3c6151316b285f40-->
?
- `cache_control` cache points (**4 maximum**) or automatic cache
- **TTL of 5 minutes** by default, refreshed every time; **1 hour** optional
- Write: **1.25×** Entry price (TTL 5 min) or **2×** (1 h); read: **0.1×** in general, even less so on some recent models
- Cost effective **from the 2e request** with the TTL of 5 minutes

Other providers automatically hide long prefixes (e.g. OpenAI).

---

Where to place the cache point in an Anthropic query, and how to verify that it serves? <!--anki:3831373663633535333531303462326639393035363139393733623433396164-->
?
Place `cache_control` **at the end of the reusable prefix**. In the API Native Anthropic Messages, `system` is a separate parameter, not a role in `messages`:
```python
response = client.messages.create(
    model=MODEL, max_tokens=512,
    system=[
        {"type": "text", "text": SYSTEM_PROMPT},
        {"type": "text", "text": DOC_REFERENCE,
         "cache_control": {"type": "ephemeral"}},
    ],
    messages=[*historical, {"role": "user", "content": question}],
)
print(response.usage.cache_read_input_tokens)
```
The snippet assumes a configured client and defined variables. Also check for cached tokens, model thresholds, and TTL; a null reading value may match the first call or a non-allowable prefix.

---

How to structure a cache prompt? <!--anki:4f51376957666f576324-->
?
- **Stable first, variable at end**: → system tools → history → question
- **No dynamic element in mind**: neither date of the day nor query ID
- **Deterministic serialization**: sorted JSON keys, tools always in the same order
- The Point of Cache **End of the shared part**, not at the end of the whole prompt

---

What silently invalidates the LLM prefix cache? <!--anki:6e785d3b6e524c4f7c69-->
?
A change can **reduce the common prefix from the divergence point**, without necessarily removing all the reusable cache. It depends on the tokens, blocks and engine rules.

Timestamping in the lead, reordered tools or rewritten history often reduce sharing. A change in weight, adapt or configuration affecting states requires a compatible cache space. Some providers impose other eligibility rules.

Observe the tokens read and written, not just a Boolean: the hit can become partial or zero. A change of byte does not universally translate into a total invalidation; check the actual serialization and tokenization.

---

Why should an agent's context be append-only? <!--anki:73484b265258215a627d-->
?
Any modification of a past message **invalidates the cache of everything that follows**. On **Addition** Instead of rewriting. To restrict the tools available, they are **Mask to Decoding** rather than removing their definition, or we pass the "mode" in a message.

This is a re-use optimization, not a rule that overrides the fix. Obsolete data, a secret, or a permission removed must be processed even if it invalidates the cache. Masking tools depends on the capabilities of the server; in any case, the application must refuse an action that is now prohibited.

---

What trap do parallel queries pose for Anthropic prompt caching? <!--anki:652c325f3b695271513b-->
?
A cache entry is only readable **once the first response starts streaming**. N requests launched at the same time with the same prefix therefore pay **All the writing**. Parade: **Pre-heat** the cache (at Anthropic, A call with `max_tokens: 0`), Make a request before others.

Observe separately **cold cache and hot cache** in a load test: a preheated benchmark hides the cost of the simultaneous start. The preheating itself adds a call and a write; it is justified if the subsequent readings cushion them. Check the usage counters and the capabilities of the model before generalizing the strategy.

---

When to choose a 1-hour TTL for Anthropic prompt caching? <!--anki:6f6f646f25692c73362f-->
?
When the difference between two requests that share the prefix is **between 5 and 60 minutes** (a user who replies after 20 minutes). Below 5 minutes, each read refreshes the TTL of 5 minutes: it stays warm on its own and costs less to write.

The choice is made on the **distribution of reuse intervals**, not just on their average. A long TTL costs more to write and may never be reread; a short TTL can cause repeated rewrites. Compare the expected cost of both options on actual sessions, with the rates and rules applicable to the model.

---

What can be hidden outside the model? <!--anki:415f533243626d51464d-->
?
- **Exact answers**: = hash key of the normalized prompt + model + parameters
- **Semantic cache** for related questions ([[82-routing-llm|routing]])
- **Embeddings**: hash of the chunk + version of the embedding model, never to re-embed
- **Results of tools, API and Retrieval**, with a TTL adapted to their freshness

A key must also reflect the relevant rights and versions. Do not blindly normalize negations, units or identifiers: "authorized" and "unauthorized" are not interchangeable answers, even if their embeddings are close.

---

How to avoid serving an outdated or false response from the cache? <!--anki:76254f61255254613b4e-->
?
- A **complete key**: model, prompt version, parameters, holding, index version RAG
- A **TTL** adapted to the freshness of the data, and a **invalidation** with each change of prompt or data
- **Do not hide** personalized or voluntarily varied responses
- A **strict threshold** for semantic cache

The TTL does not guarantee an immediate revocation. If the rights change, invalidate the entry or recheck its proofs before service. Testing the same question, two users and then removing access; a quick hit on prohibited information remains a failure.

---

What security and privacy risks do responses and prompts pose? <!--anki:4674494c5b246e5b6f36-->
?
- **Run between users** if the cache key does not include the holder
- **Time auxiliary channel** on a shared [[66-prefix-caching-radix-attention|prefix cache]]
- **Sensitive data** stored in the cache: encryption, retention time, right to be forgotten

A key must also reflect the **rights, version of the data, and perimeter of the response.** Two users on the same tenant may have different accesses. After a change of permission or deletion, invalidate the affected entries; encryption protects the storage but does not prevent serving a response to the wrong recipient.

---

How to control prompt caching in production? <!--anki:6a474d563c7128623b56-->
?
Follow **tokens reused, cost per task and TTFT**, by model and prompt version. Check eligibility threshold, TTL, routing and possible write cost.

Example: moving a variable timestamp before the common instructions breaks the shared prefix. A test with a stable prefix and long enough must see the expected reuse by the engine or supplier contract.

The second identical request is not a universal hit guarantee: asynchronous filling, foreclosure or other replicas may occur. Test with a limited wait if necessary and report the failure. Analyze a fall before incriminating the prompt; the traffic may also have changed.

---

Do not confuse: quick caching, response cache and semantic cache? <!--anki:4f5e492c7e32682c4e78-->
?
- **Prompt caching**: Re-uses the **prefix calculation** at the provider or server. The answer is always **generated**, so always right
- **Exact response cache**: returns an already generated response for a **identical** query, no appeal to the model
- **Semantic cache**: Returns an answer already generated for a query **close** to embedding. The most economical, but the only one that can **mistake** question ([[82-routing-llm|Semantic Cache]])

---

Why does a semantic cache need to be tested on almost identical questions but with opposite answers? <!--anki:6562643638356465353737373433313061336430323966316134623863363332-->
?
The **Nearembeddings** “Can I cancel before 24 hours? and "can I cancel after 24 hours? ». However, a small lexical difference can change the applicable rule.

Build pairs on negation, amount, date, identity, and contract version. Include these dimensions in the key or verify their equivalence before reuse. Measure misuses in addition to the hit rate. Reserve this cache for tasks where the equivalence of response is sufficiently verifiable; a strong similarity does not constitute proof of the same business intent.

---

What is a stampede cache in a LLM application and how to limit it? <!--anki:3337623436326133643763393434623438636330656630663764376432666530-->
?
When a popular entry expires, **many queries simultaneously recalculate the same result**. The cache reduces the average load but creates an expensive spike.

Consolidate concurrent calculations of the same key, allocate expirations, and allow for tight deadlines. Serving an old value is acceptable only if freshness and permissions allow it. Test the failure of the proprietary worker so as not to leave all clients stuck.

---

Why should the key of a response cache include more than the textual question? <!--anki:6664316432633939336130663463326138313965396364376135653234363266-->
?
The answer also depends on **holder, rights, source versions, and relevant configuration**. A key based on text alone can reuse a private or outdated response.

Choosing a key and invalidation for these dependencies, and then rechecking the privileges when necessary. Over-detailing the key reduces sharing; optimization comes after the fix. A question hash does not make the cache contents anonymous.

---

## Scenarios

Scenario: the cost of your agent has doubled overnight, without increasing traffic, and no error appears. What is your first hypothesis? <!--anki:632335685b6277747a4b-->
?
1. **Prefix cache is broken**: watch tokens read cached in `usage` fields, often dropped to zero
2. **Search for cause at the top of prompt**: added timestamp, reordered tool, unsorted JSON, changed model
3. **Check history**: A summary or deletion of past messages invalidates all of the following
4. **Correct**: stable prefix, context **append-only**, deterministic serialization
5. **Warning**: alert about the drop in the hit rate and integration test that checks that a second request reads the cache

**Trap**: look for a traffic leak while the regression is silent and error-free.

---

Scenario: you run 20 parallel queries that share the same long prefix, and you find that nothing is read cached. Why? <!--anki:7163282a2d4e30233068-->
?
1. **Cause** A cache entry becomes readable only after the first response is started. The 20 simultaneous requests all pay for writing
2. **Parade**: **Preheat** the cache with a first request, then run the others
3. **Choosing TTL**: 5 minutes is enough if the requests follow each other, one hour if the gap exceeds a few minutes
4. **Measuring the real gain**: writing is more expensive than reading, so the calculation must be done
5. **Check isolation**: the cache key must include the client, to avoid leakage ([[66-prefix-caching-radix-attention|Auxiliary Channel]])

**Trap**: conclude that prompt caching "does not work" from a test run in parallel.

---

Scenario: an answer cache saves you 30%, but support reports obsolete answers after a documentation update. How do you fix this? <!--anki:7a23736f586e37576861-->
?
1. **Review the cache key**: model, prompt version, settings, client, and most importantly **RAG index version**
2. **Invalidate** with each prompt or corpus change, rather than waiting for expiration
3. **Adjust TTL** according to the expected freshness of the data
4. **Excludes cache** personalized or voluntarily varied responses
5. **Monitoring**: Hit rate, but also reports of inappropriate responses served from the cache

**Trap**: a key based on the text of the question alone, which ignores the rest of the context.

---

## Sources

- [Anthropic — operation and limits of prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/)

- 14 November 2026 — Complete blocks, divergence and cache identity: [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/).

## Connections
- [[20-010-rag-permissions-versions|RAG: rights & versions]] — invalidate replies after update or revocation
- [[121-inference-costs|Inference costs]] — what cache saves
- [[122-finops-llm|FinOps LLM]] — caches as lever FinOps
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — the server-side mechanism
- [[35-context-engineering|Context engineering]] — the stable prefix
- [[82-routing-llm|Routing LLM]] — semantic cache and prefix affinity
- [[81-litellm-api-layer|LiteLLM]] — response cache in the gateway
- [[133-embeddings-representations|Embeddings]] — represent meaning by vectors
- [[152-pii-privacy|PII & Privacy]] — protect personal data
- [[25-chunking-contextual-retrieval|Advanced Chunking]] — Make Every Chunk Found
- [[61-kv-cache-attention|KV cache]] — memory that limits concurrency
- [[21-rag-fundamentals|RAG — Fundamentals]] — Basic Retrieval Pipeline
- [[85-agentic-protocols-map|Map of protocols]] — which protocol to which agent boundary
- [[00-moc-ai-engineering|MOC AI Engineering]]

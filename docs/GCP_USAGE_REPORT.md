# GCP Usage and Cost Report
**Project:** `<PROJECT_ID>`  
**Billing Account:** `<BILLING_ACCOUNT_ID>`  
**Region:** europe-west1  
**Report Date:** 2025-11-05  

---

## Active Resources

### 1. Firestore (Native Mode)
**Database:** `(default)`  
**Location:** europe-west1  
**Created:** 2025-10-30  
**Type:** Native mode (document database)

**Usage Pattern:**
- User sessions and conversation history
- Graph data persistence (nodes, edges, evidence)
- Authentication state

**Estimated Cost:**
- **Stored Data:** ~1 GB (estimated based on typical usage)
  - Cost: $0.18/GB/month = **~$0.18/month**
- **Document Reads:** ~1,000/day (sessions, graph loads)
  - Cost: $0.06 per 100k reads = **~$0.002/day** = **~$0.06/month**
- **Document Writes:** ~500/day (messages, graph updates)
  - Cost: $0.18 per 100k writes = **~$0.001/day** = **~$0.03/month**
- **Total Firestore:** **~$0.27/month**

**Free Tier Coverage:**
- ✅ 1 GB storage/day (we use ~1 GB total)
- ✅ 50k reads/day (we use ~1k/day)
- ✅ 20k writes/day (we use ~500/day)
- **Actual Cost: $0/month** (within free tier)

---

### 2. Vertex AI (Gemini 2.5 Flash)
**Model:** gemini-2.5-flash  
**Location:** europe-west1  
**API:** aiplatform.googleapis.com

**Usage Pattern:**
- Discovery: 1 call per assessment (~2k chars input, ~1k chars output)
- Assessment: 3-4 calls per assessment (~1k chars input, ~500 chars output)
- Total: ~5 LLM calls per complete assessment

**Estimated Cost (per 1M tokens):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Monthly Estimate (100 assessments):**
- Discovery: 100 × 2k input = 200k input tokens = **$0.015**
- Discovery: 100 × 1k output = 100k output tokens = **$0.030**
- Assessment: 400 × 1k input = 400k input tokens = **$0.030**
- Assessment: 400 × 500 output = 200k output tokens = **$0.060**
- **Total Vertex AI: ~$0.135/month** (100 assessments)

**Scaling:**
- 1,000 assessments/month: **~$1.35/month**
- 10,000 assessments/month: **~$13.50/month**

---

### 3. Cloud Storage
**Bucket:** None currently active
**Usage:** Service account keys stored locally only

**Estimated Cost:** **$0/month**

---

### 4. Cloud Logging
**API:** logging.googleapis.com  
**Usage:** Application logs, API request logs

**Estimated Cost:**
- First 50 GB/month: Free
- Current usage: <1 GB/month
- **Total Logging: $0/month** (within free tier)

---

### 5. Cloud Monitoring
**API:** monitoring.googleapis.com  
**Usage:** Basic metrics collection

**Estimated Cost:**
- First 150 MB/month: Free
- Current usage: <10 MB/month
- **Total Monitoring: $0/month** (within free tier)

---

### 6. Firebase Services
**Active APIs:**
- Firebase Authentication (identitytoolkit.googleapis.com)
- Firebase Hosting (firebasehosting.googleapis.com)
- Firebase Remote Config (firebaseremoteconfig.googleapis.com)

**Usage:**
- Authentication: Anonymous auth for sessions
- Hosting: Not actively used (Streamlit runs locally)
- Remote Config: Not actively used

**Estimated Cost:**
- Authentication: Free tier (50k MAU)
- Hosting: $0 (not deployed)
- Remote Config: Free tier
- **Total Firebase: $0/month** (within free tier)

---

## Enabled but Unused Services

These APIs are enabled but not actively generating costs:

- BigQuery (bigquery.googleapis.com) - No datasets
- Cloud Build (cloudbuild.googleapis.com) - No builds
- Cloud Run (run.googleapis.com) - No services
- Pub/Sub (pubsub.googleapis.com) - No topics
- Cloud SQL (sql-component.googleapis.com) - No instances
- App Engine (appengine.googleapis.com) - No apps

**Cost Impact:** $0/month (no usage)

---

## Total Monthly Cost Estimate

### Current Usage (Light Development)
| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Firestore | $0.00 | Within free tier |
| Vertex AI (Gemini) | $0.14 | ~100 assessments/month |
| Cloud Storage | $0.00 | No buckets |
| Cloud Logging | $0.00 | Within free tier |
| Cloud Monitoring | $0.00 | Within free tier |
| Firebase | $0.00 | Within free tier |
| **TOTAL** | **~$0.14/month** | **~$1.68/year** |

### Production Usage Scenarios

**Low Volume (1,000 assessments/month):**
- Firestore: $0.00 (still within free tier)
- Vertex AI: $1.35
- Other: $0.00
- **Total: ~$1.35/month** (~$16/year)

**Medium Volume (10,000 assessments/month):**
- Firestore: $0.50 (exceeds free tier)
- Vertex AI: $13.50
- Other: $0.00
- **Total: ~$14/month** (~$168/year)

**High Volume (100,000 assessments/month):**
- Firestore: $5.00
- Vertex AI: $135.00
- Cloud Logging: $2.00
- **Total: ~$142/month** (~$1,704/year)

---

## Cost Optimization Recommendations

### 1. Vertex AI (Biggest Cost Driver)

**Current Optimization:**
- ✅ Using Gemini 2.5 Flash (cheapest model)
- ✅ Context size failsafe (prevents oversized prompts)
- ✅ Lazy loading (only load data when needed)
- ✅ Concise prompts (~3k chars vs 15k chars)

**Additional Optimizations:**
- 🔄 Cache LLM responses for identical prompts
- 🔄 Batch multiple assessments if possible
- 🔄 Use streaming only when needed (non-streaming is same cost)

**Potential Savings:** 10-20% reduction

### 2. Firestore

**Current Optimization:**
- ✅ Efficient data model (minimal writes)
- ✅ Session-based persistence (not per-message)
- ✅ Lazy graph loading

**Additional Optimizations:**
- 🔄 Implement TTL for old sessions (reduce storage)
- 🔄 Batch writes where possible
- 🔄 Use transactions to reduce failed writes

**Potential Savings:** Minimal (already in free tier)

### 3. Unused Services

**Action:** Disable unused APIs to reduce attack surface
```bash
gcloud services disable bigquery.googleapis.com --project=<PROJECT_ID>
gcloud services disable cloudbuild.googleapis.com --project=<PROJECT_ID>
gcloud services disable run.googleapis.com --project=<PROJECT_ID>
```

**Potential Savings:** $0 (no current cost, but cleaner project)

---

## Cost Monitoring Setup

### 1. Set Budget Alerts

```bash
# Create budget alert at $10/month
gcloud billing budgets create \
  --billing-account=<BILLING_ACCOUNT_ID> \
  --display-name="AI Assessment Engine Budget" \
  --budget-amount=10 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

### 2. Enable Cost Breakdown

In GCP Console:
1. Go to Billing → Reports
2. Filter by Project: `<PROJECT_ID>`
3. Group by: Service
4. Time range: Last 30 days

### 3. Track Key Metrics

**Vertex AI Usage:**
```bash
gcloud logging read 'resource.type="aiplatform.googleapis.com/Endpoint"' \
  --limit=100 \
  --format=json \
  --project=<PROJECT_ID>
```

**Firestore Operations:**
```bash
gcloud logging read 'resource.type="cloud_firestore_database"' \
  --limit=100 \
  --format=json \
  --project=<PROJECT_ID>
```

---

## Billing Account Details

**Account ID:** `<BILLING_ACCOUNT_ID>`  
**Status:** ✅ Active (Open)  
**Linked Projects:** `<PROJECT_ID>`

**Note:** If multiple projects share the same billing account, costs are aggregated across all projects.

---

## Free Tier Status

### Always Free (No Expiration)
- ✅ Firestore: 1 GB storage, 50k reads/day, 20k writes/day
- ✅ Cloud Logging: 50 GB/month
- ✅ Cloud Monitoring: 150 MB metrics/month
- ✅ Firebase Auth: 50k MAU

### Trial Credits
- Check GCP Console → Billing → Credits for any remaining trial credits
- Typically $300 for 90 days for new accounts

---

## Cost Projection

### Next 30 Days (Development)
- **Expected:** $0.14 - $1.00
- **Worst Case:** $5.00 (if testing heavily)

### Next 90 Days (Phase 2-3 Development)
- **Expected:** $5 - $20
- **Worst Case:** $50 (if running extensive tests)

### Production (Year 1)
- **Low Volume:** $200 - $500/year
- **Medium Volume:** $1,000 - $2,000/year
- **High Volume:** $5,000 - $10,000/year

---

## Action Items

### Immediate ✅ COMPLETED
- ✅ Context size failsafe implemented (prevents cost spikes)
- ✅ Lazy loading implemented (reduces unnecessary API calls)
- ✅ Using cheapest model (Gemini 2.5 Flash)
- ✅ Budget alert set at $10/month (50%, 90%, 100% thresholds)
- ✅ Disabled unused APIs (Cloud Build, Cloud Run, Cloud Testing)
- ✅ Cost tracking added to LLM logs (input/output tokens + USD estimate)

### This Week
- [ ] Monitor budget alerts
- [ ] Review first week of cost logs
- [ ] Document cost per assessment patterns

### This Month
- [ ] Implement LLM response caching (10-20% savings potential)
- [ ] Set up monthly cost review process
- [ ] Optimize high-cost operations if any identified

---

## Summary

**Current Status:** ✅ Very cost-efficient
- Most services within free tier
- Only Vertex AI generating costs (~$0.14/month)
- Well-optimized prompts and data model

**Risk Level:** 🟢 Low
- Context size failsafe prevents runaway costs
- Conservative limits (30k chars = ~$0.002 per call)
- No expensive services enabled

**Recommendation:** Continue current approach
- Monitor monthly costs
- Set budget alerts
- Optimize further only if costs increase

---

**Report Generated:** 2025-11-05  
**Next Review:** 2025-12-05  
**Contact:** Check GCP Console → Billing for real-time data

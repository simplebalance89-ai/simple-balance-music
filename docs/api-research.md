# Simple Balance Music — API Research

**Date:** Feb 25, 2026
**Repo:** `C:\Claude\Work\simple-balance-demo\`
**File reviewed:** `server.py`

---

## 1. MusicGen Check (`/api/generate/audio`)

### Current Implementation (Lines 452-493)

```python
MUSICGEN_MODEL = "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedbd"

output = replicate.run(
    MUSICGEN_MODEL,
    input={
        "prompt": prompt,
        "duration": duration,
        "model_version": "stereo-melody-large",
    },
)
audio_url = str(output) if output else None
```

### Assessment

**Model ID:** The model string `meta/musicgen:671ac6...` pins to a specific version hash. This is correct Replicate syntax (`owner/model:version`). The model is live on Replicate at `replicate.com/meta/musicgen`.

**Parameters look correct:**
- `prompt` (string) — text description of desired music. Valid.
- `duration` (int, clamped 1-30) — seconds of audio. Valid. MusicGen supports up to 30s.
- `model_version: "stereo-melody-large"` — Valid. Available options are: `stereo-melody-large`, `stereo-large`, `melody-large`, `large`, `encode-decode`. Stereo-melody-large is the best choice (3.3B params, stereo output, melody conditioning).

**Response handling:** `replicate.run()` for MusicGen returns a `FileOutput` object. Casting to `str()` extracts the URL. This is correct — Replicate returns a temporary URL to the generated audio file.

### Issues Found

1. **Version hash may be stale.** The pinned version hash (`671ac645...`) could become outdated if Replicate updates the model. Consider using `meta/musicgen` without a version pin to always get the latest, OR periodically verify the hash is still valid. If it goes stale, Replicate returns a 404/model-not-found error.

2. **Missing optional parameters.** MusicGen also accepts `temperature` (default 1.0), `top_k` (default 250), `top_p` (default 0.0), `classifier_free_guidance` (default 3), and `output_format` (default "wav"). These could be exposed to give users more control.

3. **No melody input support.** Since `stereo-melody-large` supports melody conditioning (pass an audio file as `input_audio`), the endpoint could accept an optional audio upload for melody-guided generation. Currently text-only.

4. **No error detail on Replicate failures.** The catch block returns the raw exception string. Replicate errors can include billing/quota issues that should be handled more gracefully.

5. **MUSICGEN_MODEL constant is also used only here** but is defined at module level near the AudD section (line 63). Minor organizational note.

**Verdict: Implementation is functional and correct.** The model ID, parameters, and response parsing all work. The version hash staleness is the main risk.

---

## 2. Event Discovery APIs

### Current State
The `/api/events` endpoint (lines 319-353) uses Azure OpenAI to GENERATE FAKE events. It asks GPT to hallucinate "realistic" events with `link: '#'` placeholders. This needs to be replaced with real event data.

---

### 2A. Ticketmaster Discovery API

**Verdict: BEST OPTION. Use this.**

| Item | Detail |
|------|--------|
| **URL** | `https://app.ticketmaster.com/discovery/v2/events.json` |
| **Auth** | API key as query param `?apikey={key}` |
| **Free tier** | Yes — 5,000 requests/day, 2 requests/second |
| **Signup** | https://developer.ticketmaster.com/ — instant API key |
| **Cost** | Free for Discovery API |

**Key search parameters:**
- `keyword` — free text search ("house music", "techno", artist name)
- `classificationName=music` — filter to music events only
- `city` — filter by city name
- `latlong` + `radius` + `unit` — geo-based search (e.g., `latlong=25.7617,-80.1918&radius=50&unit=miles`)
- `startDateTime` / `endDateTime` — ISO 8601 date range
- `genreId` or `subGenreId` — filter by specific genre
- `size` — results per page (max 200)
- `sort` — `date,asc` or `relevance,desc`

**Response data (per event in `_embedded.events[]`):**
- `name` — event name
- `dates.start.localDate` / `localTime` — event date/time
- `_embedded.venues[0].name` — venue name
- `_embedded.venues[0].city.name` — city
- `_embedded.venues[0].address.line1` — address
- `_embedded.attractions[].name` — artist/lineup names
- `url` — direct Ticketmaster ticket link
- `images[]` — event images in multiple sizes
- `priceRanges[].min` / `max` — ticket price range
- `classifications[].genre.name` — genre

**Example request:**
```
GET https://app.ticketmaster.com/discovery/v2/events.json?apikey=KEY&classificationName=music&city=Miami&size=10&sort=date,asc
```

**Pros:** Massive event database, real ticket links, venue details, images, free tier is generous.
**Cons:** Primarily Ticketmaster/Live Nation venues. May miss smaller/underground events.

---

### 2B. DICE (dice.fm)

**Verdict: NOT VIABLE for integration.**

| Item | Detail |
|------|--------|
| **Public API** | NO — no public developer API for event discovery |
| **Partner API** | GraphQL API exists but requires partner relationship + API token from MIO (their internal platform) |
| **What it covers** | Ticket holder data, event finances — NOT event search/discovery |
| **Workarounds** | Third-party scrapers exist on Apify (Dice.fm Scraper) but violate TOS and are fragile |

**Alternatives to DICE data:**
- Ticketmaster covers most large events DICE would list
- For underground/independent events that DICE specializes in, Resident Advisor (RA) is the closest equivalent but also lacks a public API
- Bandsintown covers artist-centric event discovery

**Recommendation:** Skip DICE. Not worth the effort.

---

### 2C. Eventbrite API

**Verdict: LIMITED USE — Event search endpoint was deprecated in 2020.**

| Item | Detail |
|------|--------|
| **URL** | `https://www.eventbriteapi.com/v3/` |
| **Auth** | OAuth token in header `Authorization: Bearer {token}` |
| **Free tier** | Yes — 1,000 calls/hour, 48,000 calls/day |
| **Critical issue** | `GET /v3/events/search/` was REMOVED in Feb 2020 |

**What still works:**
- `GET /v3/events/:event_id/` — get event by ID
- `GET /v3/venues/:venue_id/events/` — list events at a venue
- `GET /v3/organizations/:org_id/events/` — list events by organizer

**What does NOT work:**
- General event search by keyword/location/genre — **GONE**

**Recommendation:** Not viable as a primary event source. You'd need to know specific venue or organizer IDs upfront, which defeats the purpose of discovery. Skip for Events Radar.

---

### 2D. Songkick API

**Verdict: UNCERTAIN — platform had issues, API access unclear.**

| Item | Detail |
|------|--------|
| **URL** | `https://api.songkick.com/api/3.0/` |
| **Auth** | API key as query param `?apikey={key}` |
| **Status** | Songkick was acquired by Warner Music in 2017, had operational issues in 2018. The website still exists and the API docs are still online, but new API key registration may be closed |
| **Data** | 6M+ concerts, upcoming and past |

**Endpoints (if accessible):**
- `/events.json?apikey=KEY&location=geo:{lat},{lng}` — events by location
- `/search/artists.json?apikey=KEY&query={name}` — search artists
- `/artists/{id}/calendar.json` — upcoming events for artist

**Recommendation:** Don't rely on it. Registration may be closed, and the platform's long-term viability is uncertain. Use Ticketmaster + Bandsintown instead.

---

### 2E. Bandsintown API

**Verdict: GOOD SECONDARY OPTION — artist-centric events.**

| Item | Detail |
|------|--------|
| **URL** | `https://rest.bandsintown.com/` |
| **Auth** | `app_id` query parameter |
| **Free tier** | Yes — free for displaying event data. Must get app_id from Bandsintown |
| **Registration** | Artists get API keys via Bandsintown for Artists dashboard (Settings > General > Get API Key). For general dev use, contact Bandsintown for approval |
| **TOS requirement** | Must display Bandsintown branding, need written consent |

**Endpoints:**
- `GET /artists/{artist_name}/events?app_id={id}` — upcoming events for artist
- `GET /artists/{artist_name}?app_id={id}` — artist info
- Date filtering: `&date=upcoming` or `&date=2026-01-01,2026-06-01`

**Response data (per event):**
```json
{
  "id": "12345",
  "datetime": "2026-09-10T20:00:00",
  "title": "Event Name",
  "description": "...",
  "url": "https://www.bandsintown.com/e/12345?app_id=...",
  "venue": {
    "name": "Madison Square Garden",
    "city": "New York",
    "region": "NY",
    "country": "US",
    "latitude": "40.7505",
    "longitude": "-73.9934"
  },
  "lineup": ["Artist 1", "Artist 2"],
  "offers": [{"type": "Tickets", "url": "...", "status": "available"}]
}
```

**Pros:** Artist-focused (great for "follow this artist" features), includes lineup, ticket links, venue geo.
**Cons:** Must search by artist name, not by location/genre. No "show me all events in Miami" query. Requires app_id approval.

---

### Event API Recommendation for Events Radar

**Primary: Ticketmaster Discovery API** — location + genre search, real ticket links, free tier, instant signup.
**Secondary: Bandsintown** — artist-centric supplement. "Find events for artists in your library."
**Skip: DICE, Eventbrite (search deprecated), Songkick (uncertain).**

Architecture: Replace the AI-hallucinated `/api/events` endpoint with a real Ticketmaster call. Add a Bandsintown layer for artist-specific event tracking. Keep Azure OpenAI as a fallback for event recommendations/curation text, not event data.

---

## 3. Spotify Per-User Architecture (Authorization Code Flow)

### Current State
The app uses **Client Credentials flow** (lines 575-606). This gives server-to-server access with NO user context. Available endpoints: search, public playlists, audio features (limited), recommendations (deprecated).

### CRITICAL: Spotify API Deprecations (Nov 27, 2024)

Spotify deprecated several endpoints that the app currently uses:

| Endpoint | Status | Impact on SBM |
|----------|--------|---------------|
| `GET /v1/recommendations` | **DEPRECATED** | `/api/spotify/recommendations` endpoint is BROKEN for new apps |
| `GET /v1/audio-features/{id}` | **DEPRECATED** | `/api/spotify/audio-features/{track_id}` endpoint is BROKEN for new apps |
| `GET /v1/audio-features?ids=` | **DEPRECATED** | Batch audio features in `/api/spotify/playlist/{id}/tracks` is BROKEN for new apps |
| `GET /v1/audio-analysis/{id}` | **DEPRECATED** | Not used in SBM, but FYI |

**Grandfathering:** Apps that had extended quota approval BEFORE Nov 27, 2024 can still use these. New apps get 403 errors. If SBM's Spotify app was created after that date, these endpoints will not work.

**This is a major issue regardless of auth flow change.** Switching to Authorization Code flow does NOT restore access to deprecated endpoints.

---

### What Changes with Authorization Code Flow

#### Auth Flow Steps

1. **User clicks "Connect Spotify"** in SBM UI
2. **Redirect to Spotify auth page:**
   ```
   GET https://accounts.spotify.com/authorize?
     client_id={CLIENT_ID}&
     response_type=code&
     redirect_uri={REDIRECT_URI}&
     scope={SCOPES}&
     state={RANDOM_STATE}
   ```
3. **User approves** and Spotify redirects back to `{REDIRECT_URI}?code={AUTH_CODE}&state={STATE}`
4. **Server exchanges code for tokens:**
   ```
   POST https://accounts.spotify.com/api/token
   Body: grant_type=authorization_code&code={AUTH_CODE}&redirect_uri={REDIRECT_URI}
   Header: Authorization: Basic {base64(client_id:client_secret)}
   ```
   Returns: `access_token`, `refresh_token`, `expires_in` (3600s)
5. **Refresh when expired:**
   ```
   POST https://accounts.spotify.com/api/token
   Body: grant_type=refresh_token&refresh_token={REFRESH_TOKEN}
   ```

**Alternative: PKCE flow** (no client_secret needed, better for SPAs). Uses `code_verifier` + `code_challenge` instead.

#### Redirect URI Setup
- Register in Spotify Developer Dashboard under app settings
- For Render: `https://simple-balance-demo.onrender.com/api/spotify/callback`
- For local dev: `http://localhost:8000/api/spotify/callback`
- Must be EXACT match (no wildcards)

#### Scopes Needed

| Scope | What it unlocks |
|-------|-----------------|
| `user-read-recently-played` | GET /v1/me/player/recently-played — last 50 tracks |
| `user-top-read` | GET /v1/me/top/artists, /v1/me/top/tracks — user's top items (short/medium/long term) |
| `user-library-read` | GET /v1/me/tracks — user's saved/liked tracks |
| `user-library-modify` | PUT /v1/me/tracks — save tracks to library |
| `playlist-read-private` | GET /v1/me/playlists — user's private playlists |
| `playlist-modify-public` | POST /v1/users/{id}/playlists, POST /v1/playlists/{id}/tracks — create playlists, add tracks |
| `playlist-modify-private` | Same as above but for private playlists |
| `user-read-playback-state` | GET /v1/me/player — what's currently playing |
| `user-read-currently-playing` | GET /v1/me/player/currently-playing |

**Recommended scope string for SBM:**
```
user-read-recently-played user-top-read user-library-read playlist-read-private playlist-modify-public playlist-modify-private
```

#### New Endpoints Available (per-user)

| Endpoint | What | Use in SBM |
|----------|------|------------|
| `GET /v1/me/player/recently-played` | Last 50 tracks played | "Your Recent" feed, session history |
| `GET /v1/me/top/artists?time_range=short_term` | Top artists (4 weeks/6 months/all time) | Personalized recommendations, genre profiling |
| `GET /v1/me/top/tracks?time_range=medium_term` | Top tracks | Set builder seeds, taste analysis |
| `GET /v1/me/tracks` | User's liked songs | Library integration, bulk analysis |
| `GET /v1/me/playlists` | All playlists (inc. private) | Playlist browser with audio features |
| `POST /v1/users/{id}/playlists` | Create new playlist | "Export Set" feature — save built sets as Spotify playlists |
| `POST /v1/playlists/{id}/tracks` | Add tracks to playlist | Populate exported playlists |
| `GET /v1/me` | User profile | Display name, avatar, account type |

#### Session Management — Token Storage Per User

**Option A: In-memory dict (simplest, Render-compatible)**
```python
user_sessions = {}  # {session_id: {access_token, refresh_token, expires_at, spotify_user_id}}
```
- Use a secure httponly cookie with a session ID
- Tokens live in server memory
- **Problem:** Render free tier sleeps after 15 min inactivity. Memory wipes on sleep/restart. Users must re-auth after every cold start.

**Option B: Encrypted file storage**
```python
# Write tokens to disk (Render has ephemeral disk on free tier — also wipes on deploy)
# NOT recommended for free tier
```

**Option C: Client-side encrypted tokens**
- Store encrypted refresh_token in browser localStorage
- Send with each request, server decrypts and uses
- Survives Render restarts
- Must encrypt with a server-side key (env var)
- **Best option for Render free tier**

**Option D: External DB (Redis/Postgres)**
- Render offers free Redis (90 day limit) and free Postgres (90 day limit)
- Proper session management but adds complexity
- Best for production, overkill for demo

#### Render Free Tier Feasibility

| Concern | Assessment |
|---------|------------|
| OAuth redirect works? | Yes — FastAPI handles redirects fine |
| HTTPS required? | Yes — Render provides HTTPS by default |
| Memory persistence? | NO — free tier sleeps, memory wipes. Use client-side token storage or external DB |
| Cold start latency? | ~30-60 seconds on wake. User hits "Connect Spotify", app wakes, redirect happens. Acceptable |
| Multiple users? | Yes — each user gets their own tokens. In-memory works while app is awake |
| Custom domain? | Not needed — `simple-balance-demo.onrender.com` works as redirect URI |

**Verdict: Feasible on Render free tier** with client-side encrypted token storage. Users will need to re-authenticate if localStorage is cleared, but the experience is smooth otherwise.

#### Implementation Estimate

New endpoints to add to `server.py`:
1. `GET /api/spotify/login` — generates auth URL, redirects user
2. `GET /api/spotify/callback` — handles redirect, exchanges code, sets session cookie
3. `GET /api/spotify/me` — returns user profile
4. `GET /api/spotify/me/recent` — recently played
5. `GET /api/spotify/me/top/artists` — top artists
6. `GET /api/spotify/me/top/tracks` — top tracks
7. `GET /api/spotify/me/library` — saved tracks
8. `POST /api/spotify/me/playlists` — create playlist
9. `GET /api/spotify/logout` — clear session

Plus frontend: "Connect Spotify" button, auth state management, user-specific UI sections.

**Estimated effort:** ~4-6 hours for backend + frontend integration.

---

## Summary Table

| API | Viable? | Free? | Best For | Priority |
|-----|---------|-------|----------|----------|
| **Ticketmaster Discovery** | YES | Yes (5K/day) | Events Radar (location + genre search) | HIGH — implement first |
| **Bandsintown** | YES (with approval) | Yes | Artist-specific event tracking | MEDIUM — supplement Ticketmaster |
| **Eventbrite** | NO | N/A | Search deprecated in 2020 | SKIP |
| **DICE** | NO | N/A | No public API | SKIP |
| **Songkick** | UNCERTAIN | Unknown | Registration may be closed | SKIP |
| **Spotify Auth Code** | YES | Yes | Per-user library, playlists, personalization | HIGH — major feature unlock |
| **MusicGen (Replicate)** | YES (working) | Pay-per-use | Audio generation | DONE — minor improvements only |

### Critical Alert: Spotify Deprecations
The `/api/spotify/recommendations` and `/api/spotify/audio-features` endpoints in the current codebase will return **403 errors** if the Spotify app was created after Nov 27, 2024. Verify the app creation date. If affected, these features need alternative implementations (e.g., use Azure OpenAI for recommendations, use a third-party audio analysis service for BPM/key detection).

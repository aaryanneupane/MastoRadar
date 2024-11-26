
# MastoRadar - The Decentralized Recommender System for Mastodon

MastoRadar provides a decentralized recommender system for Mastodon, allowing users to explore an additional timeline of toots recommended for themselves based on interractions.

## Timelines mapped to Mastadon.social website

- **Home timeline can be fetched from**: `mastodon.timeline_home()`
- **Live Feed - "All" can be fetched from**: `mastodon.timeline_public()`
- **Live Feed - "This server" can be fetched from**: `mastodon.timeline_local()`
- **The Explore page cannot be fetched as a viewable timeline directly, but can be fetched as a JSON from**:

```javascript
  fetch('https://mastodon.social/api/v1/trends/statuses', {
    headers: {
      Authorization: `Bearer ACCESS-TOKEN`,
    },
  })

# Architecture

## Overview
The system is split into a Vue 3 frontend and a FastAPI backend. The backend indexes folders and archives under a configurable root, and the frontend consumes JSON and image streams.

For Docker deployment, the production packaging is a single container: Vue static assets are built first, then served by Nginx in the same container that also runs the FastAPI backend.

## Backend Modules
- `app/api`: HTTP endpoints (auth, users, media)
- `app/services/db.py`: SQLite access
- `app/services/auth.py`: password hashing + JWT
- `app/services/deps.py`: auth dependencies
- `app/services/fs_indexer.py`: directory listing, pagination, and folder tree
- `app/services/archive_reader.py`: ZIP/7Z/RAR listing and file streaming
- `app/services/thumbnailer.py`: thumbnail generation and cache (folder + archive)
- `app/utils/path.py`: safe path resolution under `PHOTO_ROOT`

## Frontend Modules
- `src/api/client.ts`: API client, token handling
- `src/store/auth.ts`: login state
- `src/store/gallery.ts`: state for folder/archives with pagination and tree
- `src/views`: main screens (login, library, archive, image viewer, collections, users)
- `src/components/ImageBrowserSection.vue`: shared image browser shell for folder, archive, and collection image sections
- `src/components/FolderGrid.vue`: folder/archive cover cards with explicit cover loading state
- `src/components/ImageGrid.vue`: masonry image grid with explicit thumbnail loading state
- `src/components`: reusable UI blocks, sidebar tree, browser shell, and masonry grid
- `src/pwa/registerSW.ts`: service worker registration
- `src/pwa/updateState.ts`: app-wide PWA update prompt state

## Frontend UX Notes
- Archive browsing, collection image browsing, and normal folder image browsing intentionally share one browser-shell component so mobile/PWA layout changes only need to be maintained in one place.
- Cover cards and image cards track `loading | ready | failed` explicitly instead of relying only on DOM class toggles from `load` events. This prevents placeholder layers from sticking when images are restored from cache or when list nodes are reused.
- Privacy reveal removes blur smoothly without a compensating scale transform, which avoids the visible “jump” when tapping to remove the mask.
- The login screen includes lightweight product branding (`IV` mark + `轻图`) but keeps authentication flow unchanged.

## Data Flow
1. User logs in and receives a JWT token.
2. Frontend requests `/api/tree` and `/api/folder` with auth token.
3. Backend enforces allowed paths per user.
4. Images and thumbnails include `token` query so `<img>` can load.
5. Thumbnails are generated on demand and cached in `THUMB_CACHE`.
6. In PWA mode, the frontend registers a service worker and exposes a manual refresh action when a newer asset set has been downloaded.

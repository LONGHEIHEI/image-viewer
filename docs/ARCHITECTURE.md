# Architecture

## Overview
The system is split into a Vue 3 frontend and a FastAPI backend. The backend indexes folders and archives under a configurable root, and the frontend consumes JSON and image streams.

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
- `src/views`: main screens (login, library, archive, image viewer, users)
- `src/components`: reusable UI blocks, sidebar tree, and masonry grid

## Data Flow
1. User logs in and receives a JWT token.
2. Frontend requests `/api/tree` and `/api/folder` with auth token.
3. Backend enforces allowed paths per user.
4. Images and thumbnails include `token` query so `<img>` can load.
5. Thumbnails are generated on demand and cached in `THUMB_CACHE`.

import { defineStore } from 'pinia'
import {
  createFavorite,
  deleteFavorite,
  getArchive,
  getCollectionArchive,
  getCollectionFolder,
  getFavorites,
  getFolder,
  getTree,
  type ArchiveListing,
  type FavoriteItem,
  type FavoritePayload,
  type FolderListing,
  type TreeNode
} from '../api/client'
import { buildFavoriteKey, favoriteToPayload } from '../utils/favorites'

export const useGalleryStore = defineStore('gallery', {
  state: () => ({
    currentFolder: '' as string,
    listing: null as FolderListing | null,
    archivePath: '' as string,
    archiveListing: null as ArchiveListing | null,
    tree: null as TreeNode | null,
    loading: false,
    treeLoading: false,
    favoritesLoading: false,
    favoritesLoaded: false,
    error: '' as string,
    treeError: '' as string,
    collectionId: null as number | null,
    collectionName: '' as string,
    collectionPrivacyEnabled: false,
    collectionFolder: '' as string,
    collectionListing: null as FolderListing | null,
    collectionArchivePath: '' as string,
    collectionArchiveListing: null as ArchiveListing | null,
    favorites: [] as FavoriteItem[]
  }),
  actions: {
    async loadFolder(path = '', page = 1, pageSize = 20, append = false) {
      this.loading = true
      this.error = ''
      try {
        this.currentFolder = path
        const data = await getFolder(path, page, pageSize)
        if (append && this.listing && this.listing.folder === data.folder) {
          this.listing = {
            ...data,
            folders: this.listing.folders,
            archives: this.listing.archives,
            images: [...this.listing.images, ...data.images]
          }
        } else {
          this.listing = data
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : '未知错误'
      } finally {
        this.loading = false
      }
    },
    async loadArchive(path: string, page = 1, pageSize = 20, append = false) {
      this.loading = true
      this.error = ''
      try {
        this.archivePath = path
        const data = await getArchive(path, page, pageSize)
        if (append && this.archiveListing && this.archiveListing.archive === data.archive) {
          this.archiveListing = {
            ...data,
            files: [...this.archiveListing.files, ...data.files]
          }
        } else {
          this.archiveListing = data
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : '未知错误'
      } finally {
        this.loading = false
      }
    },
    async loadTree(depth = 2) {
      this.treeLoading = true
      this.treeError = ''
      try {
        this.tree = await getTree('', depth)
      } catch (err) {
        this.treeError = err instanceof Error ? err.message : '未知错误'
      } finally {
        this.treeLoading = false
      }
    },
    async loadCollectionFolder(
      collectionId: number,
      path = '',
      page = 1,
      pageSize = 20,
      append = false,
      view: 'folder' | 'flat' = 'folder'
    ) {
      this.loading = true
      this.error = ''
      try {
        this.collectionId = collectionId
        this.collectionFolder = path
        const data = await getCollectionFolder(collectionId, path, page, pageSize, view)
        if (append && this.collectionListing && this.collectionListing.folder === data.folder) {
          this.collectionListing = {
            ...data,
            folders: this.collectionListing.folders,
            archives: this.collectionListing.archives,
            images: [...this.collectionListing.images, ...data.images]
          }
        } else {
          this.collectionListing = data
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : '未知错误'
      } finally {
        this.loading = false
      }
    },
    async loadCollectionArchive(
      collectionId: number,
      path: string,
      page = 1,
      pageSize = 20,
      append = false
    ) {
      this.loading = true
      this.error = ''
      try {
        this.collectionId = collectionId
        this.collectionArchivePath = path
        const data = await getCollectionArchive(collectionId, path, page, pageSize)
        if (append && this.collectionArchiveListing && this.collectionArchiveListing.archive === data.archive) {
          this.collectionArchiveListing = {
            ...data,
            files: [...this.collectionArchiveListing.files, ...data.files]
          }
        } else {
          this.collectionArchiveListing = data
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : '未知错误'
      } finally {
        this.loading = false
      }
    },
    async loadFavorites(force = false) {
      if (this.favoritesLoaded && !force) return
      this.favoritesLoading = true
      try {
        this.favorites = await getFavorites()
        this.favoritesLoaded = true
      } catch {
        this.favorites = []
        this.favoritesLoaded = false
      } finally {
        this.favoritesLoading = false
      }
    },
    clearFavorites() {
      this.favorites = []
      this.favoritesLoaded = false
      this.favoritesLoading = false
    },
    hasFavorite(key: string) {
      return this.favorites.some((item) => buildFavoriteKey(item) === key)
    },
    async addFavorite(payload: FavoritePayload) {
      await createFavorite(payload)
      const item: FavoriteItem = {
        id: 0,
        user_id: 0,
        source_kind: payload.source_kind,
        collection_id: payload.collection_id ?? null,
        container_path: payload.container_path || '',
        item_path: payload.item_path,
        folder_path: payload.folder_path || '',
        view_mode: payload.view_mode === 'flat' ? 'flat' : 'folder',
        item_name: payload.item_name || '',
        created_at: new Date().toISOString()
      }
      const nextKey = buildFavoriteKey(item)
      this.favorites = [item, ...this.favorites.filter((current) => buildFavoriteKey(current) !== nextKey)]
      this.favoritesLoaded = true
    },
    async removeFavorite(payload: Pick<FavoritePayload, 'source_kind' | 'collection_id' | 'container_path' | 'item_path'>) {
      await deleteFavorite(payload)
      const nextKey = buildFavoriteKey({
        source_kind: payload.source_kind,
        collection_id: payload.collection_id ?? null,
        container_path: payload.container_path || '',
        item_path: payload.item_path
      })
      this.favorites = this.favorites.filter((item) => buildFavoriteKey(item) !== nextKey)
    },
    async toggleFavorite(payload: FavoritePayload) {
      const key = buildFavoriteKey(payload)
      if (this.hasFavorite(key)) {
        await this.removeFavorite(payload)
        return false
      }
      await this.addFavorite(payload)
      return true
    },
    async removeFavoriteItem(item: FavoriteItem) {
      await this.removeFavorite(favoriteToPayload(item))
    }
  }
})

import { defineStore } from 'pinia'
import {
  getFolder,
  getArchive,
  getTree,
  getCollectionFolder,
  getCollectionArchive,
  type FolderListing,
  type ArchiveListing,
  type TreeNode
} from '../api/client'

export const useGalleryStore = defineStore('gallery', {
  state: () => ({
    currentFolder: '' as string,
    listing: null as FolderListing | null,
    archivePath: '' as string,
    archiveListing: null as ArchiveListing | null,
    tree: null as TreeNode | null,
    loading: false,
    treeLoading: false,
    error: '' as string,
    treeError: '' as string,
    collectionId: null as number | null,
    collectionFolder: '' as string,
    collectionListing: null as FolderListing | null,
    collectionArchivePath: '' as string,
    collectionArchiveListing: null as ArchiveListing | null
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
      append = false
    ) {
      this.loading = true
      this.error = ''
      try {
        this.collectionId = collectionId
        this.collectionFolder = path
        const data = await getCollectionFolder(collectionId, path, page, pageSize)
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
    }
  }
})

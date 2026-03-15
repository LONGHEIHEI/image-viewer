import { defineStore } from 'pinia'
import {
  getFolder,
  getArchive,
  getTree,
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
    treeError: '' as string
  }),
  actions: {
    async loadFolder(path = '', page = 1, pageSize = 60, append = false) {
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
    async loadArchive(path: string, page = 1, pageSize = 80, append = false) {
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
    }
  }
})

from pydantic import BaseModel
from typing import List

class FolderItem(BaseModel):
    name: str
    path: str

class FolderListing(BaseModel):
    folder: str
    folders: List[FolderItem]
    images: List[FolderItem]
    archives: List[FolderItem]
    page: int
    page_size: int
    total_images: int
    has_more: bool

class ArchiveFile(BaseModel):
    name: str
    path: str

class ArchiveListing(BaseModel):
    archive: str
    files: List[ArchiveFile]
    page: int
    page_size: int
    total_files: int
    has_more: bool


class TreeNode(BaseModel):
    name: str
    path: str
    type: str
    children: List['TreeNode'] = []


TreeNode.model_rebuild()

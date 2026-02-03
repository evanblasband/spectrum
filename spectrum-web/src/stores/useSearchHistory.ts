import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface SearchHistoryItem {
  url: string
  title: string | null
  source: string | null
  searchedAt: string
  success: boolean
  errorMessage?: string
}

interface SearchHistoryState {
  history: SearchHistoryItem[]
  addToHistory: (item: Omit<SearchHistoryItem, 'searchedAt'>) => void
  clearHistory: () => void
  removeFromHistory: (url: string) => void
}

const MAX_HISTORY_ITEMS = 10

export const useSearchHistory = create<SearchHistoryState>()(
  persist(
    (set, get) => ({
      history: [],

      addToHistory: (item) => {
        const currentHistory = get().history
        
        // Remove existing entry for this URL if it exists
        const filteredHistory = currentHistory.filter(h => h.url !== item.url)
        
        // Add new item at the beginning
        const newItem: SearchHistoryItem = {
          ...item,
          searchedAt: new Date().toISOString(),
        }
        
        // Keep only the last MAX_HISTORY_ITEMS
        const newHistory = [newItem, ...filteredHistory].slice(0, MAX_HISTORY_ITEMS)
        
        set({ history: newHistory })
      },

      clearHistory: () => {
        set({ history: [] })
      },

      removeFromHistory: (url) => {
        set({ history: get().history.filter(h => h.url !== url) })
      },
    }),
    {
      name: 'spectrum-search-history',
    }
  )
)
